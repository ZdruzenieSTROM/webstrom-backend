from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator


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

    # TODO: change school to ChoiceField from model School
    school = models.CharField(max_length=128)

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
