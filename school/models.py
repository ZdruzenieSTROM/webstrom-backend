from django.db import models
from base.managers import UnspecifiedValueManager


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
