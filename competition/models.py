import datetime

import pdf2image
from django.contrib.sites.models import Site
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.timezone import now

from base.validators import school_year_validator


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

    def __str__(self):
        return self.name

    @cached_property
    def semester_set(self):
        return self.event_set.exclude(semester__isnull=True)

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
    # sum_method =  # NO FOKEN IDEA

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

    def get_user_results(self):
        pass


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
        return f'{self.series.semester.competition.name}-{self.series.semester.year}-{self.series.semester.season[0]}S-S{self.series.order} - {self.order}. úloha'

    def get_mean_point(self):
        pass


class Grade(models.Model):
    class Meta:
        verbose_name = 'ročník účastníka'
        verbose_name_plural = 'ročníky účastníka'
        ordering = ['years_until_graduation']

    name = models.CharField(
        max_length=32,
        verbose_name='názov ročníku'
    )
    tag = models.CharField(
        max_length=2,
        unique=True,
        verbose_name='skratka'
    )
    years_until_graduation = models.PositiveSmallIntegerField(
        verbose_name='počet rokov do maturity'
    )
    is_active = models.BooleanField(
        verbose_name="aktuálne používaný ročník"
    )

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
        upload_to='solutions/', verbose_name='účastnícke riešenie')

    corrected_solution_path = models.FileField(
        upload_to='solutions/corrected/', verbose_name='opravené riešenie')

    score = models.PositiveSmallIntegerField(verbose_name='body')

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
