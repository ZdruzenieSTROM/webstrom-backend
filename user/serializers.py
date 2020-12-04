from django.contrib.auth import authenticate

from rest_framework import serializers, exceptions
from allauth.account import app_settings

from user.models import User, TokenModel


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = '"email" a "heslo" musia byť vyplnené.'
            raise exceptions.ValidationError(msg)

        return user

    def get_auth_user(self, email, password):
        return self._validate_email(email, password)

    def validate_auth_user_status(self, user):
        if not user.is_active:
            msg = 'User nie je aktívny'
            raise exceptions.ValidationError(msg)

    def validate_email_verification_status(self, user):
        if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
            email_address = user.emailaddress_set.get(email=user.email)
            if not email_address.verified:
                raise serializers.ValidationError('Email nie je overený.')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = self.get_auth_user(email, password)

        if not user:
            msg = 'Nie je možné prihlásiť sa zadanými prihlasovacími údajmi.'
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        self.validate_email_verification_status(user)

        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = TokenModel
        fields = ('key',)


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', ]  # 'first_name', 'last_name'
