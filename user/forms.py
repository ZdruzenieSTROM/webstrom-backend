from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from user.models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'school',
            'phone',
            'parent_phone'
        )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'school',
            'phone',
            'parent_phone',
            'email_verified'
        )
