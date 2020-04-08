from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from base.validators import phone_number_validator
from base.managers import UnspecifiedValueManager


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email musí byť nastavený')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser musí byť správca')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser musí mať is_superuser=True')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'používateľ'
        verbose_name_plural = 'používatelia'

    email = models.EmailField(
        unique=True, max_length=255, verbose_name='email')
    verified_email = models.BooleanField(
        default=False, verbose_name='overený email')

    is_staff = models.BooleanField(
        default=False, verbose_name='správcovský prístup')
    is_active = models.BooleanField(default=True, verbose_name='je aktívny')

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Profile(models.Model):
    class Meta:
        verbose_name = 'profil'
        verbose_name_plural = 'profily'

    user = models.OneToOneField('user.User', on_delete=models.CASCADE)

    first_name = models.CharField(max_length=32, verbose_name='krstné meno')
    last_name = models.CharField(max_length=32, verbose_name='priezvisko')
    nickname = models.CharField(
        max_length=32, blank=True, null=True, verbose_name='prezývka')

    school = models.ForeignKey(
        'user.School', on_delete=models.CASCADE, verbose_name='škola')

    year_of_graduation = models.PositiveSmallIntegerField(
        verbose_name='rok maturity')

    phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        validators=[phone_number_validator],
        verbose_name='telefónne číslo',
        help_text='Telefonné číslo oddelené medzerami po trojčísliach \
        na začiatku s predvoľbou.'
    )
    parent_phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        validators=[phone_number_validator],
        verbose_name='telefónne číslo na rodiča',
        help_text='Telefonné číslo oddelené medzerami po trojčísliach \
        na začiatku s predvoľbou.'
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class County(models.Model):
    class Meta:
        verbose_name = 'kraj'
        verbose_name_plural = 'kraje'

    code = models.AutoField(primary_key=True, verbose_name='kód')
    name = models.CharField(max_length=30, verbose_name='názov')

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        return self.name


class District(models.Model):
    class Meta:
        verbose_name = 'okres'
        verbose_name_plural = 'okresy'

    code = models.AutoField(primary_key=True, verbose_name='kód')
    name = models.CharField(max_length=30, verbose_name='názov')
    abbreviation = models.CharField(max_length=2, verbose_name='skratka')

    county = models.ForeignKey(
        County, on_delete=models.CASCADE, verbose_name='kraj')

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        return self.name


class School(models.Model):
    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'

    code = models.AutoField(primary_key=True, verbose_name='kód')
    name = models.CharField(max_length=100, verbose_name='názov')
    abbreviation = models.CharField(max_length=10, verbose_name='skratka')

    street = models.CharField(max_length=100, verbose_name='ulica')
    city = models.CharField(max_length=100, verbose_name='obec')
    zip_code = models.CharField(max_length=6, verbose_name='PSČ')
    email = models.CharField(max_length=50, verbose_name='email', null=True)

    district = models.ForeignKey(
        District, on_delete=models.CASCADE, verbose_name='okres')

    objects = UnspecifiedValueManager(unspecified_value_pk=0)

    def __str__(self):
        if self.street and self.city:
            return f'{ self.name }, { self.street }, { self.city }'

        return self.name

    def stitok(self):
        return f'\\stitok{{{ self.nazov }}}{{{ self.city }}}' \
               f'{{{ self.zip }}}{{{ self.street }}}'
