from allauth.account.signals import email_confirmed
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    # pylint: disable=E1101

    username = None
    first_name = None
    last_name = None

    email = models.EmailField('email', unique=True)
    verified_email = models.BooleanField(
        verbose_name='overený email', default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []


@receiver(email_confirmed)
def email_verified(request, **kwargs):
    user = User.objects.get(email=kwargs['email_address'].email)

    user.verified_email = True

    user.save()


TokenModel = Token
