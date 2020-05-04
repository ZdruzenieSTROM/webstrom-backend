import datetime

import pdf2image
from django.contrib.sites.models import Site
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.timezone import now
from user.models import User
from base.validators import school_year_validator
import competition.utils as utils


class Competition(models.Model):
    class Meta:
        verbose_name = 'súťaž'
        verbose_name_plural = 'súťaže'

    name = models.CharField(
        max_length=50,
        verbose_name='názov'
    )

    start_year = models.PositiveSmallIntegerField(
        verbose_name='rok prvého ročníka súťaže',
        blank=True
    )
    sites = models.ManyToManyField(Site)
    competition_type = models.PositiveSmallIntegerField(
        choices=[(0, 'Seminar'), (1, 'Single day competition'), (2, 'Other')],
        verbose_name='typ súťaže'
    )
    min_years_until_graduation = models.PositiveSmallIntegerField(
        verbose_name='Minimálny počet rokov do maturity',
        help_text='Horná hranica na účasť v súťaži. '
        'Zadáva sa v počte rokov do maturity. Ak najstraší, kto môže riešiť súťaž je deviatak, zadá sa 4.',
        null=True
    )

    def can_user_participate(self, user):
        if self.min_years_until_graduation:
            return user.profile.year_of_graduation-utils.get_school_year_start_by_date() \
                >= self.min_years_until_graduation

        return True

    def __str__(self):
        return self.name

    @cached_property
    def semester_set(self):
        return Semester.objects.filter(competition=self.pk).all()

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
        max_length=50, verbose_name='označenie štítku pre riešiteľa')
    upper_bound = models.DurationField(
        verbose_name='maximálna dĺžka omeškania')
    comment = models.TextField(verbose_name='komentár pre opravovateľa')

    def __str__(self):
        return self.name


class Event(models.Model):
    class Meta:
        verbose_name = 'ročník súťaže'
        verbose_name_plural = 'ročníky súťaží'
        ordering = ['-school_year', ]

    competition = models.ForeignKey(
        Competition, null=True, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(blank=True, verbose_name='ročník')
    school_year = models.CharField(
        max_length=10, blank=True, verbose_name='školský rok', validators=[school_year_validator])
    start = models.DateTimeField(verbose_name='dátum začiatku súťaže')
    end = models.DateTimeField(verbose_name='dátum konca súťaže')

    @cached_property
    def is_active(self):
        return self.semester.series_set.filter(complete=False).count() > 0

    def is_user_registered(self,user_id):
        return UserEventRegistration.objects.filter(event=self.pk,user=user_id).count()>0

    @property
    def registered_users(self):
        return User.objects.filter(usereventregistration_set__event=self.pk).all()
         

    def __str__(self):
        if self.semester:
            return str(self.semester)
        else:
            return f'{self.competition.name}, {self.year}. ročník'


class Semester(Event):
    class Meta:
        verbose_name = 'semester'
        verbose_name_plural = 'semestre'

        ordering = ['-year', 'season_code']

    SEASON_CHOICES = (
        (0, 'Zimný'),
        (1, 'Letný'),
    )

    season_code = models.PositiveSmallIntegerField(choices=SEASON_CHOICES)
    late_tags = models.ManyToManyField(LateTag, verbose_name='', blank=True)

    @cached_property
    def season(self):
        return self.get_season_code_display()

    def __str__(self):
        return f'{self.competition.name}, {self.year}. ročník - {self.season} semester'


class Series(models.Model):
    class Meta:
        verbose_name = 'séria'
        verbose_name_plural = 'série'

        ordering = ['semester', 'order', ]

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name='poradie série')
    deadline = models.DateTimeField(verbose_name='termín série')
    complete = models.BooleanField(verbose_name='séria uzavretá')
    sum_method = models.CharField(max_length=50,
        blank=True,
        null=True,
        verbose_name='Súčtová metóda',
        choices=utils.SERIES_SUM_METHODS
        )

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
    def num_problems(self):
        return self.problem_set.count()

    def _create_user_dict(self,sum_func,user,user_solutions):
        return {
                'rank_start':0,
                'rank_end':0,
                'rank_changed':True,
                'name': f'{user.user.profile.first_name} ', #TODO: FullName
                'school': user.school,
                'grade': user.class_level.tag,
                'points': utils.solutions_to_list_of_points_pretty(user_solutions),
                'total': sum_func(user_solutions,user),
                'solutions': user_solutions
            }

    def results(self):
        sum_func = getattr(utils, self.sum_method or '', utils.series_simple_sum)
        results = []
        
        solutions = Solution.objects.only('user_semester_registration', 'problem', 'score').filter(problem__series=self.pk).order_by('user_semester_registration','problem').select_related('user_semester_registration','problem')

        current_user = None
        user_solutions = [None] * self.num_problems

        for solution in solutions:
            if current_user!=solution.user_semester_registration:
                if current_user:
                    #Bolo dokončené spracovanie jedného usera
                    #Zbali usera a a nahodi ho do vysledkov
                    results.append(self._create_user_dict(sum_func,current_user,user_solutions))
                # vytvori prazdny list s riešeniami
                current_user = solution.user_semester_registration
                user_solutions = [None] * self.num_problems
            
            # Spracuj riešenie
            user_solutions[solution.problem.order - 1] = solution

        # Uloz posledneho usera
        if current_user:
            results.append(self._create_user_dict(sum_func,current_user,user_solutions))

        
        results.sort(key=lambda x: x['total'], reverse=True)
        return results



class Problem(models.Model):
    class Meta:
        verbose_name = 'úloha'
        verbose_name_plural = 'úlohy'

        ordering = ['series', 'order', ]

    text = models.TextField(verbose_name='znenie úlohy')
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        verbose_name='úloha zaradená do série'
    )
    order = models.PositiveSmallIntegerField(verbose_name='poradie v sérii')

    def __str__(self):
        return f'{self.series.semester.competition.name}-{self.series.semester.year}' \
            f'-{self.series.semester.season[0]}S-S{self.series.order} - {self.order}. úloha'

    def get_mean_point(self):
        pass


class Grade(models.Model):
    class Meta:
        verbose_name = 'ročník účastníka'
        verbose_name_plural = 'ročníky účastníka'
        ordering = ['years_until_graduation', ]

    name = models.CharField(max_length=32, verbose_name='názov ročníku')
    tag = models.CharField(max_length=2, unique=True, verbose_name='skratka')
    years_until_graduation = models.SmallIntegerField(
        verbose_name='počet rokov do maturity')
    is_active = models.BooleanField(
        verbose_name='aktuálne používaný ročník')

    def get_year_of_graduation_by_date(self, date=None):
        return utils.get_school_year_end_by_date(date) + self.years_until_graduation

    def __str__(self):
        return self.name


class UserEventRegistration(models.Model):
    class Meta:
        verbose_name = 'registrácia užívateľa na akciu'
        verbose_name_plural = 'registrácie užívateľov na akcie'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    school = models.ForeignKey(
        'user.School', on_delete=models.SET_NULL, null=True)
    class_level = models.ForeignKey(Grade, on_delete=models.CASCADE)
    event = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} v {self.event}'


class Solution(models.Model):
    class Meta:
        verbose_name = 'riešenie'
        verbose_name_plural = 'riešenia'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_semester_registration = models.ForeignKey(
        UserEventRegistration,
        on_delete=models.CASCADE
    )
    solution_path = models.FileField(
        upload_to='solutions/', 
        verbose_name='účastnícke riešenie', 
        null=True, 
        blank=True
    )

    corrected_solution_path = models.FileField(
        upload_to='solutions/corrected/', 
        verbose_name='opravené riešenie', 
        null=True, 
        blank=True
        )

    score = models.PositiveSmallIntegerField(verbose_name='body', null=True, blank=True)

    uploaded_at = models.DateTimeField(
        auto_now=True, verbose_name='nahrané dňa')

    # V prípade, že riešenie prišlo po termíne nastaví sa na príslušný tag
    late_tag = models.ForeignKey(
        LateTag,
        on_delete=models.SET_NULL,
        verbose_name='',
        null=True,
        blank=True)

    is_online = models.BooleanField(
        verbose_name='internetové riešenie'
    )

    def __str__(self):
        return f'Riešiteľ: {self.user_semester_registration} - úloha: {self.problem}'

# Časopisy, brožúry, pozvánky, výsledkové listiny ...


class Publication(models.Model):
    class Meta:
        verbose_name = 'publikácia'
        verbose_name_plural = 'publikácie'

    event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)
    pdf_file = models.FileField(
        upload_to='publications/'
    )
    order = models.PositiveSmallIntegerField()
    # TODO: Premyslieť ukladanie
    @property
    def get_thumbnail_path(self):
        return f'publications/thumbnails/{self.file_name}'

    @property
    def get_publication_path(self):
        return f'publications/{self.file_name}'

    @property
    def file_name(self):
        f'{self.event.competition}-{self.event.year}-{self.order}-{self.pk}.pdf'

    def __str__(self):
        return f'{self.event.competition}-{self.event.year}-{self.order}'


"""
@receiver(post_save, sender=Publication)
def generate_leaflet_thumbnail(sender, instance, created, **kwargs):
    source_path = instance.get_publication_path()
    dest_path = instance.get_thumbnail_path()
    pdf2image.convert_from_path(source_path)

"""
