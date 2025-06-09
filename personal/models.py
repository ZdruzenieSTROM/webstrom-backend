from django.apps import apps
from django.conf import settings
from django.db import models

from base.managers import UnspecifiedValueManager
from base.validators import phone_number_validator


class County(models.Model):
    class Meta:
        verbose_name = 'kraj'
        verbose_name_plural = 'kraje'

    code = models.AutoField(verbose_name='kód', primary_key=True)
    name = models.CharField(verbose_name='názov', max_length=30)

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        return self.name


def unspecified_county():
    return County.objects.get_unspecified_value()


class District(models.Model):
    class Meta:
        verbose_name = 'okres'
        verbose_name_plural = 'okresy'

    code = models.AutoField(verbose_name='kód', primary_key=True)
    name = models.CharField(verbose_name='názov', max_length=30)
    abbreviation = models.CharField(verbose_name='skratka', max_length=2)

    county = models.ForeignKey(
        County, verbose_name='kraj',
        on_delete=models.SET(unspecified_county)
    )

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        return self.name


def unspecified_district():
    return District.objects.get_unspecified_value()


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
    email = models.CharField(verbose_name='email',
                             max_length=50, blank=True, null=True)

    district = models.ForeignKey(
        District, verbose_name='okres',
        on_delete=models.SET(unspecified_district)
    )

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    @property
    def printable_zip_code(self):
        return self.zip_code[:3]+' '+self.zip_code[3:]

    def __str__(self):
        if self.street and self.city:
            return f'{self.name}, {self.street}, {self.city}'
        return self.name

    @property
    def stitok(self):
        return f'\\stitok{{{self.name}}}{{{self.city}}}' \
            f'{{{self.printable_zip_code}}}{{{self.street}}}'


def unspecified_school():
    return School.objects.get_unspecified_value()


class Profile(models.Model):
    class Meta:
        verbose_name = 'profil'
        verbose_name_plural = 'profily'

    first_name = models.CharField(verbose_name='krstné meno', max_length=150)

    last_name = models.CharField(verbose_name='priezvisko', max_length=150)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        related_name='profile'
    )

    school = models.ForeignKey(
        School, on_delete=models.SET(unspecified_school),
        verbose_name='škola'
    )

    year_of_graduation = models.PositiveSmallIntegerField(
        verbose_name='rok maturity')

    phone = models.CharField(
        verbose_name='telefónne číslo', max_length=32, blank=True, null=True,
        validators=[phone_number_validator],
        help_text='Telefonné číslo v medzinárodnom formáte (napr. +421 123 456 789).')

    parent_phone = models.CharField(
        verbose_name='telefónne číslo na rodiča', max_length=32, blank=True, null=True,
        validators=[phone_number_validator],
        help_text='Telefonné číslo v medzinárodnom formáte (napr. +421 123 456 789).')

    @property
    def grade(self):
        return apps.get_model('competition', 'Grade').get_grade_by_year_of_graduation(
            year_of_graduation=self.year_of_graduation
        ).pk

    @grade.setter
    def grade(self, value):
        self.year_of_graduation = apps.get_model('competition', 'Grade').get(
            pk=value).get_year_of_graduation_by_date()

    def get_full_name(self):
        return f'{self.first_name.strip()} {self.last_name.strip()}'

    def get_full_name_camel_case(self):
        return f'{self.first_name.strip()}{self.last_name.strip()}'

    def __str__(self):
        return f'{self.get_full_name()} ({self.user})'


class OtherSchoolRequest(models.Model):
    class Meta:
        verbose_name = 'Požiadavok na založenie školy'
        verbose_name_plural = 'Požiadavky na založenie školy'

    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name='other_school_request')
    school_info = models.TextField(
        verbose_name='Požadovaná škola na pridanie')

    def __str__(self):
        return str(self.profile)
