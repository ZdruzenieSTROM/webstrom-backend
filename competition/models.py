import datetime
import os
from io import BytesIO
from operator import itemgetter

import pdf2image
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.timezone import now

from base.managers import UnspecifiedValueManager
from base.models import RestrictedFileField
from base.utils import mime_type
from base.validators import phone_number_validator, school_year_validator
from competition import utils


class County(models.Model):
    class Meta:
        verbose_name = 'kraj'
        verbose_name_plural = 'kraje'

    code = models.AutoField(verbose_name='kód', primary_key=True)
    name = models.CharField(verbose_name='názov', max_length=30)

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        return self.name


class District(models.Model):
    class Meta:
        verbose_name = 'okres'
        verbose_name_plural = 'okresy'

    code = models.AutoField(verbose_name='kód', primary_key=True)
    name = models.CharField(verbose_name='názov', max_length=30)
    abbreviation = models.CharField(verbose_name='skratka', max_length=2)

    county = models.ForeignKey(
        County, verbose_name='kraj',
        on_delete=models.SET(County.objects.get_unspecified_value))

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        return self.name


class School(models.Model):
    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'

    code = models.AutoField(verbose_name='kód', primary_key=True)
    name = models.CharField(verbose_name='názov', max_length=100)
    abbreviation = models.CharField(verbose_name='skratka', max_length=10)

    street = models.CharField(verbose_name='ulica', max_length=100)
    city = models.CharField(verbose_name='obec', max_length=100)
    zip_code = models.CharField(verbose_name='PSČ', max_length=6)
    email = models.CharField(verbose_name='email', max_length=50, blank=True)

    district = models.ForeignKey(
        District, verbose_name='okres',
        on_delete=models.SET(District.objects.get_unspecified_value))

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    @property
    def printable_zip_code(self):
        return self.zip_code[:3]+' '+self.zip_code[3:]

    def __str__(self):
        if self.street and self.city:
            return f'{ self.name }, { self.street }, { self.city }'
        return self.name

    @property
    def stitok(self):
        return f'\\stitok{{{ self.name }}}{{{ self.city }}}' \
               f'{{{ self.printable_zip_code }}}{{{ self.street }}}'


class Profile(models.Model):
    class Meta:
        verbose_name = 'profil'
        verbose_name_plural = 'profily'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    nickname = models.CharField(
        verbose_name='prezývka', max_length=32, blank=True, )

    school = models.ForeignKey(
        School, on_delete=models.SET(School.objects.get_unspecified_value),
        verbose_name='škola')

    year_of_graduation = models.PositiveSmallIntegerField(
        verbose_name='rok maturity')

    phone = models.CharField(
        verbose_name='telefónne číslo', max_length=32, blank=True,
        validators=[phone_number_validator],
        help_text='Telefonné číslo v medzinárodnom formáte (napr. +421 123 456 789).')

    parent_phone = models.CharField(
        verbose_name='telefónne číslo na rodiča', max_length=32, blank=True,
        validators=[phone_number_validator],
        help_text='Telefonné číslo v medzinárodnom formáte (napr. +421 123 456 789).')

    gdpr = models.BooleanField(
        verbose_name='súhlas so spracovaním osobných údajov', default=False)

    def __str__(self):
        return str(self.user)


class Competition(models.Model):
    class Meta:
        verbose_name = 'súťaž'
        verbose_name_plural = 'súťaže'

    COMPETITION_TYPE_CHOICES = [
        (0, 'Seminár'),
        (1, 'Jednodňová súťaž'),
        (2, 'Iné'),
    ]

    name = models.CharField(verbose_name='názov', max_length=50)
    start_year = models.PositiveSmallIntegerField(
        verbose_name='rok prvého ročníka súťaže', blank=True)

    sites = models.ManyToManyField(Site)

    competition_type = models.PositiveSmallIntegerField(
        verbose_name='typ súťaže', choices=COMPETITION_TYPE_CHOICES)

    min_years_until_graduation = models.PositiveSmallIntegerField(
        verbose_name='Minimálny počet rokov do maturity', null=True,
        help_text='Horná hranica na účasť v súťaži. '
        'Zadáva sa v počte rokov do maturity. '
        'Ak najstraší, kto môže riešiť súťaž je deviatak, zadá sa 4.')

    def can_user_participate(self, user):
        if self.min_years_until_graduation:
            return user.profile.year_of_graduation-utils.get_school_year_start_by_date() \
                >= self.min_years_until_graduation
        return True

    def __str__(self):
        return self.name

    @cached_property
    def semester_set(self):
        return Semester.objects.filter(competition=self.pk)

    @classmethod
    def get_seminar_by_site(cls, site):
        return get_object_or_404(cls, sites=site, competition_type=0)

    @classmethod
    def get_seminar_by_current_site(cls):
        return cls.get_seminar_by_site(Site.objects.get_current())


class LateTag(models.Model):
    class Meta:
        verbose_name = 'omeškanie'
        verbose_name_plural = 'omeškanie'

    name = models.CharField(
        verbose_name='označenie štítku pre riešiteľa', max_length=50)
    upper_bound = models.DurationField(
        verbose_name='maximálna dĺžka omeškania')
    comment = models.TextField(verbose_name='komentár pre opravovateľa')

    def __str__(self):
        return self.name


class Event(models.Model):
    # pylint: disable=no-member
    class Meta:
        verbose_name = 'ročník súťaže'
        verbose_name_plural = 'ročníky súťaží'
        ordering = ['-school_year', ]

    competition = models.ForeignKey(
        Competition, null=True, on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField(verbose_name='ročník', blank=True)
    school_year = models.CharField(
        verbose_name='školský rok', max_length=10, blank=True,
        validators=[school_year_validator])

    start = models.DateTimeField(verbose_name='dátum začiatku súťaže')
    end = models.DateTimeField(verbose_name='dátum konca súťaže')

    def is_user_registered(self, user):
        return EventRegistration.objects.filter(event=self.pk, user=user).exists()

    @property
    def registered_profiles(self):
        return Profile.objects.filter(eventregistration_set__event=self.pk)

    def __str__(self):
        if self.semester:
            return str(self.semester)
        else:
            return f'{self.competition.name}, {self.year}. ročník'


class Semester(Event):
    class Meta:
        verbose_name = 'semester'
        verbose_name_plural = 'semestre'
        ordering = ['-year', '-season_code', ]

    SEASON_CHOICES = [
        (0, 'Zimný'),
        (1, 'Letný'),
    ]

    season_code = models.PositiveSmallIntegerField(choices=SEASON_CHOICES)
    late_tags = models.ManyToManyField(
        LateTag, verbose_name='Stavy omeškania', blank=True)

    def get_first_series(self):
        return self.series_set.get(order=1)

    def get_second_series(self):
        return self.series_set.get(order=2)

    @cached_property
    def season(self):
        return self.get_season_code_display()

    @cached_property
    def season_short(self):
        return self.get_season_code_display()[:3].lower()

    @cached_property
    def is_active(self):
        return self.series_set.filter(complete=False).exists()

    @property
    def is_at_least_one_series_open(self):
        return self.series_set.filter(can_submit=True).exists()

    def __str__(self):
        return f'{self.competition.name}, {self.year}. ročník - {self.season} semester'

    def _merge_profile(self, old, new, problems_in_old, problems_in_new):
        if not old:
            new['solutions'] = [None]*problems_in_old+new['solutions']
            new['points'] = ['-']*problems_in_old+new['points']
            new['subtotal'].append(0)
            return new
        elif not new:
            old['solutions'] += [None]*problems_in_new
            old['points'] += ['-']*problems_in_new
            old['subtotal'].append(0)
            return old

        else:
            # mergnutie dvoch zip
            solutions0 = []
            solutions1 = []
            for a in old['solutions']:
                solutions0.append(a[0])
                solutions1.append(a[1])
            for a in new['solutions']:
                solutions0.append(a[0])
                solutions1.append(a[1])
            old['solutions'] = zip(solutions0, solutions1)

            old['points'] += new['points']
            old['subtotal'].append(new['total'])
            old['total'] = sum(old['subtotal'])
            return old

    def _merge_results(
            self,
            current_results,
            series_results,
            problems_in_current,
            problems_in_series):
        # Zmerguje riadky výsledkov. Predpokladá že obe results su usporiadané podľa usera
        if current_results:
            merged_results = []
            i, j = 0, 0
            while i < len(current_results) and j < len(series_results):
                if current_results[i]['profile'] == series_results[j]['profile']:
                    merged_results.append(self._merge_profile(
                        current_results[i], series_results[j],
                        problems_in_current, problems_in_series))
                    i += 1
                    j += 1
                elif current_results[i]['profile'] > series_results[j]['profile']:
                    merged_results.append(self._merge_profile(
                        None, series_results[j], problems_in_current, problems_in_series))
                    j += 1
                else:
                    merged_results.append(self._merge_profile(
                        current_results[i], None, problems_in_current, problems_in_series))
                    i += 1
            while i < len(current_results):
                merged_results.append(self._merge_profile(
                    current_results[i], None, problems_in_current, problems_in_series))
                i += 1
            while j < len(series_results):
                merged_results.append(self._merge_profile(
                    None, series_results[j], problems_in_current, problems_in_series))
                j += 1
            return merged_results

        return series_results

    def results_with_ranking(self, show_only_last_series_points=False):
        current_results = None
        curent_number_of_problems = 0
        for series in self.series_set.all():
            series_result = series.results()
            count = series.num_problems
            current_results = self._merge_results(
                current_results, series_result, curent_number_of_problems, count)
            curent_number_of_problems += count
        current_results.sort(key=itemgetter('total'), reverse=True)
        current_results = utils.rank_results(current_results)
        return current_results

    def get_schools(self, offline_users_only=False):
        if offline_users_only:
            return School.objects.filter(eventregistration__event=self.pk)\
                .filter(eventregistration__solution__is_online=False)\
                .distinct()\
                .order_by('city', 'street')
        else:
            return School.objects.filter(eventregistration__event=self.pk)\
                .distinct()\
                .order_by('city', 'street')


class Series(models.Model):
    class Meta:
        verbose_name = 'séria'
        verbose_name_plural = 'série'
        ordering = ['semester', '-order', ]

    semester = models.ForeignKey(
        Semester, verbose_name='semester', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name='poradie série')

    deadline = models.DateTimeField(verbose_name='termín série')
    complete = models.BooleanField(verbose_name='séria uzavretá')

    sum_method = models.CharField(
        verbose_name='Súčtová metóda', max_length=50, blank=True,
        choices=utils.SERIES_SUM_METHODS)

    def __str__(self):
        return f'{self.semester} - {self.order}. séria'

    @property
    def is_past_deadline(self):
        return now() > self.deadline

    @property
    def time_to_deadline(self):
        remaining_time = self.deadline - now()

        if remaining_time.total_seconds() < 0:
            return datetime.timedelta(0)
        else:
            return remaining_time

    @property
    def can_submit(self):
        max_late_tag_value = self.semester.late_tags.aggregate(
            models.Max('upper_bound'))['upper_bound__max']
        if not max_late_tag_value:
            max_late_tag_value = datetime.timedelta(0)
        return now() < self.deadline + max_late_tag_value

    def get_actual_late_flag(self):
        if not self.is_past_deadline:
            return None
        if not self.can_submit:
            return None
        return self.semester.late_tags.filter(upper_bound__gte=now()-self.deadline)\
            .order_by('upper_bound')\
            .first()

    @property
    def num_problems(self):
        return self.problem_set.count()

    # Generuje jeden riadok poradia ako slovník atribútov
    def _create_profile_dict(self, sum_func, semester_registration, profile_solutions):
        # list primary keys uloh v aktualnom semestri
        problems_pk_list = []
        for problem in self.problem_set.all():
            problems_pk_list.append(problem.pk)

        return {
            # Poradie - horná hranica, v prípade deleného miesto(napr. 1.-3.) ide o nižšie miesto(1)
            'rank_start': 0,
            # Poradie - dolná hranica, v prípade deleného miesto(napr. 1.-3.) ide o vyššie miesto(3)
            'rank_end': 0,
            # Indikuje či sa zmenilo poradie od minulej priečky, slúži na delené miesta
            'rank_changed': True,
            # primary key riešiteľovej registrácie do semestra
            'semester_registration_pk': semester_registration.pk,
            'profile': semester_registration.profile,                # Profil riešiteľa
            'school': semester_registration.school,                  # Škola
            'grade': semester_registration.grade.tag,          # Značka stupňa
            'points': utils.solutions_to_list_of_points_pretty(profile_solutions),
            # Súčty bodov po sériách
            'subtotal': [sum_func(profile_solutions, semester_registration)],
            # Celkový súčet za danú entitu
            'total': sum_func(profile_solutions, semester_registration),
            # zipnutý zoznam riešení a pk príslušných problémov,
            # aby ich bolo možné prelinkovať z poradia do admina
            # a získať pk problému pri none riešení
            'solutions': zip(profile_solutions, problems_pk_list)
        }

    def results(self):
        sum_func = getattr(utils, self.sum_method or '',
                           utils.series_simple_sum)
        results = []

        solutions = Solution.objects.only('semester_registration', 'problem', 'score')\
            .filter(problem__series=self.pk)\
            .order_by('semester_registration', 'problem')\
            .select_related('semester_registration', 'problem')

        current_profile = None
        profile_solutions = [None] * self.num_problems

        for solution in solutions:
            if current_profile != solution.semester_registration:
                if current_profile:
                    # Bolo dokončené spracovanie jedného usera
                    # Zbali usera a a nahodi ho do vysledkov
                    results.append(self._create_profile_dict(
                        sum_func, current_profile, profile_solutions))
                # vytvori prazdny list s riešeniami
                current_profile = solution.semester_registration
                profile_solutions = [None] * self.num_problems

            # Spracuj riešenie
            profile_solutions[solution.problem.order - 1] = solution

        # Uloz posledneho usera
        if current_profile:
            results.append(self._create_profile_dict(
                sum_func, current_profile, profile_solutions))

        return results

    def results_with_ranking(self):
        results = self.results()
        results.sort(key=itemgetter('total'), reverse=True)
        results = utils.rank_results(results)
        return results


class Problem(models.Model):
    class Meta:
        verbose_name = 'úloha'
        verbose_name_plural = 'úlohy'

        ordering = ['series', 'order', ]

    text = models.TextField(verbose_name='znenie úlohy')
    order = models.PositiveSmallIntegerField(verbose_name='poradie v sérii')
    series = models.ForeignKey(
        Series, verbose_name='úloha zaradená do série',
        related_name='problems',
        on_delete=models.CASCADE,)

    def __str__(self):
        return f'{self.series.semester.competition.name}-{self.series.semester.year}' \
            f'-{self.series.semester.season[0]}S-S{self.series.order} - {self.order}. úloha'

    def get_stats(self):
        stats = {}
        stats['histogram'] = []
        total_solutions = 0
        total_points = 0
        for score in range(10):
            count = self.solution_set.filter(score=score).count()
            total_solutions += count
            total_points += count*score
            stats['histogram'].append({'score': score, 'count': count})
        stats['num_solutions'] = total_solutions

        stats['mean'] = total_points / \
            total_solutions if total_solutions else '?'
        return stats


class Grade(models.Model):
    class Meta:
        verbose_name = 'ročník účastníka'
        verbose_name_plural = 'ročníky účastníka'
        ordering = ['years_until_graduation', ]

    name = models.CharField(verbose_name='názov ročníku', max_length=32)
    tag = models.CharField(verbose_name='skratka', max_length=2, unique=True)
    years_until_graduation = models.SmallIntegerField(
        verbose_name='počet rokov do maturity')
    is_active = models.BooleanField(
        verbose_name='aktuálne používaný ročník')

    objects = UnspecifiedValueManager(unspecified_value_pk=13)

    def get_year_of_graduation_by_date(self, date=None):
        return utils.get_school_year_end_by_date(date) + self.years_until_graduation

    @staticmethod
    def get_grade_by_year_of_graduation(year_of_graduation, date=None):
        years_until_graduation = year_of_graduation - \
            utils.get_school_year_end_by_date(date)

        try:
            grade = Grade.objects.get(
                years_until_graduation=years_until_graduation)
        except Grade.DoesNotExist:
            grade = Grade.objects.get_unspecified_value()

        return grade

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    class Meta:
        verbose_name = 'registrácia užívateľa na akciu'
        verbose_name_plural = 'registrácie užívateľov na akcie'
        constraints = [
            UniqueConstraint(fields=['profile', 'event'],
                             name='single_registration_in_event'),
        ]

    profile = models.ForeignKey(
        Profile, verbose_name='profil', on_delete=models.CASCADE)
    school = models.ForeignKey(
        School, verbose_name='škola', on_delete=models.SET_NULL, null=True)
    grade = models.ForeignKey(
        Grade, verbose_name='ročník', on_delete=models.CASCADE)
    event = models.ForeignKey(
        Semester, verbose_name='semester', on_delete=models.CASCADE)
    votes = models.SmallIntegerField(verbose_name='hlasy', default=0)

    @staticmethod
    def get_registration_by_profile_and_event(profile, event):
        try:
            registration = EventRegistration.objects.get(
                profile=profile, event=event)
        except EventRegistration.DoesNotExist:
            registration = None

        return registration

    def __str__(self):
        return f'{ self.profile.user.get_full_name() } @ { self.event }'


class Solution(models.Model):
    class Meta:
        verbose_name = 'riešenie'
        verbose_name_plural = 'riešenia'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    semester_registration = models.ForeignKey(
        EventRegistration, on_delete=models.CASCADE)

    solution = models.FileField(
        verbose_name='účastnícke riešenie', blank=True, upload_to='solutions/')
    corrected_solution = models.FileField(
        verbose_name='opravené riešenie', blank=True, upload_to='solutions/corrected/')

    score = models.PositiveSmallIntegerField(
        verbose_name='body', null=True)

    uploaded_at = models.DateTimeField(
        verbose_name='dátum pridania', auto_now_add=True)

    # V prípade, že riešenie prišlo po termíne nastaví sa na príslušný tag
    late_tag = models.ForeignKey(
        LateTag, verbose_name='Stavy omeškania',
        on_delete=models.SET_NULL, null=True)

    is_online = models.BooleanField(
        verbose_name='internetové riešenie', default=False)

    def __str__(self):
        return f'Riešiteľ: { self.semester_registration } - úloha { self.problem }'


class Publication(models.Model):
    """
    Reprezentuje výsledky, brožúrku alebo akýkoľvek materiál
    zverejnený k nejakému Eventu. Časopisy vyčleňujeme
    do špeciálnej podtriedy SemesterPublication
    """

    class Meta:
        verbose_name = 'publikácia'
        verbose_name_plural = 'publikácie'

    name = models.CharField(max_length=30, blank=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class SemesterPublication(Publication):
    class Meta:
        verbose_name = 'časopis'
        verbose_name_plural = 'časopisy'

    order = models.PositiveSmallIntegerField()
    file = RestrictedFileField(
        upload_to='publications/semester_publication/%Y',
        content_types=['application/pdf'],
        verbose_name='súbor')
    thumbnail = models.ImageField(
        upload_to='publications/thumbnails/%Y',
        blank=True,
        verbose_name='náhľad')

    def validate_unique(self, *args, **kwargs):
        super(SemesterPublication, self).validate_unique(*args, **kwargs)
        e = self.event
        if Publication.objects.filter(event=e, semesterpublication__isnull=False) \
                .filter(~Q(semesterpublication=self.pk), semesterpublication__order=self.order) \
                .exists():
            raise ValidationError({
                'order': 'Časopis s týmto číslom už v danom semestri existuje',
            })

    def generate_thumbnail(self, forced=False):
        if mime_type(self.file) != 'application/pdf':
            return

        if self.thumbnail and not forced:
            return

        with self.file.open(mode='rb') as file:
            pil_image = pdf2image.convert_from_bytes(
                file.read(), first_page=1, last_page=1)[0]

        png_image_bytes = BytesIO()
        pil_image.save(png_image_bytes, format='png')
        png_image_bytes.seek(0)

        thumbnail_filename = os.path.splitext(
            os.path.basename(self.file.name))[0] + '.png'

        if self.thumbnail:
            self.thumbnail.delete()

        self.thumbnail.save(
            thumbnail_filename, ContentFile(png_image_bytes.read()))

    def __str__(self):
        return self.name

    def generate_name(self, forced=False):
        if self.name and not forced:
            return

        self.name = f'{self.event.competition}-{self.event.year}-{self.order}'
        self.save()


class UnspecifiedPublication(Publication):
    class Meta:
        verbose_name = 'iná publikácia'
        verbose_name_plural = 'iné publikácie'

    file = RestrictedFileField(
        upload_to='publications/%Y',
        content_types=['application/pdf', 'application/zip'],
        verbose_name='súbor')

    def generate_name(self, forced=False):
        if self.name and not forced:
            return

        self.name = f'{self.event.competition}-{self.event.year}'
        self.save()

    def __str__(self):
        return self.name


@receiver(post_save, sender=SemesterPublication)
def make_thumbnail_on_creation(sender, instance, created, **kwargs):
    # pylint: disable=unused-argument
    if created:
        instance.generate_thumbnail()


@receiver(post_save, sender=SemesterPublication)
@receiver(post_save, sender=UnspecifiedPublication)
def make_name_on_creation(sender, instance, created, **kwargs):
    # pylint: disable=unused-argument
    if created:
        instance.generate_name()
