from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        verbose_name = 'používateľ'
        verbose_name_plural = 'používatelia'

    username = models.CharField(
        max_length=8, default='not_used')
    email = models.EmailField(
        unique=True, max_length=255, verbose_name='email')
    verified_email = models.BooleanField(
        default=False, verbose_name='overený email')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return f'{ self.get_full_name() } <{ self.email }>'
