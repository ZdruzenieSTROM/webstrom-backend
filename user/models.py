from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator


class County(models.Model):
    class Meta:
        verbose_name = 'kraj'
        verbose_name_plural = 'kraje'

    code = models.IntegerField(primary_key=True, verbose_name='kód')
    name = models.CharField(max_length=30, verbose_name='názov')

    def __str__(self):
        return self.name


class District(models.Model):
    class Meta:
        verbose_name = 'okres'
        verbose_name_plural = 'okresy'

    code = models.IntegerField(primary_key=True, verbose_name='kód')
    name = models.CharField(max_length=30, verbose_name='názov')
    county = models.ForeignKey(County, on_delete=models.SET_NULL)
    abbreviation = models.CharField(
        max_length=2, verbose_name='skratka okresu')

    def __str__(self):
        return self.name


class School(models.Model):
    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'

    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    # TODO: dať do zoznamu škôl psč?
    zip_code = models.CharField(max_length=6, null=True)
    email = models.CharField(max_length=50)
    district = models.ForeignKey(District, on_delete=models.SET_NULL)

    def __str__(self):
        # TODO: Nejaky pekny vypis skoly
        # TODO: dočasne
        return f'{ self.name }, { self.street }, { self.city }'

    def stitok(self):
        return f'\stitok{{{ self.nazov }}}{{{ self.city }}}{{{ self.zip }}}{{{ self.street }}}' 


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Používateľ musí mať nastavený email.')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='e-mail',
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name='overený e-mail'
    )

    first_name = models.CharField(
        max_length=32,
        verbose_name='krstné meno'
    )
    last_name = models.CharField(
        max_length=32,
        verbose_name='priezvisko'
    )

    nick_name = models.CharField(
        max_length=32,
        verbose_name='prezývka'
    )
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)

    phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^\+42(1|0)( \d{3}){3}$',
                message='Telefónne číslo musí byť vo formáte +421 123 456 789.',
            ),
        ],
        verbose_name='telefónne číslo',
        help_text='Telefonné číslo oddelené medzerami po trojčísliach \
        na začiatku s predvoľbou.'
    )
    parent_phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^\+42(1|0)( \d{3}){3}$',
                message='Telefónne číslo musí byť vo formáte +421 123 456 789.',
            ),
        ],
        verbose_name='telefónne číslo na rodiča',
        help_text='Telefonné číslo oddelené medzerami po trojčísliach \
        na začiatku s predvoľbou.'
    )

    last_login = models.DateTimeField(
        verbose_name='posledné prihlásenie',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='je aktívny'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='správcovský prístup'
    )

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = 'používateľ'
        verbose_name_plural = 'používatelia'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
