from django.contrib.auth import authenticate

from rest_framework import serializers, exceptions
from allauth.account import app_settings

from user.models import User, TokenModel

# TODO: presunúť importy
from django.contrib.auth import authenticate, get_user_model
from personal.models import Profile
from allauth.account.adapter import get_adapter


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
    Serializer pre Token model.
    """

    class Meta:
        model = TokenModel
        fields = ('key',)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer pre Profile
    """

    class Meta:
        model = Profile
        read_only_fields = ('first_name', 'last_name', 'year_of_graduation')
        exclude = ('user',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer pre User model spolu s Profile modelom
    """

    profile = ProfileSerializer(label='')

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    class Meta:
        model = get_user_model()
        fields = ('pk', 'email', 'profile')
        read_only_fields = ('email',)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')

        # Profile by mal byť stále vytvorený pomocou post_save User signálu.
        # Pre prípad, že sa tak nestalo, vytvorí sa Profile
        if not instance.profile:
            UserProfile.objects.create(user=instance, **profile_data)

        # Update Profile
        # Nie všetky polia v modeloch User a Profile sú editovateľné cez API.
        instance.profile.nickname = profile_data.get(
            'nickname', instance.profile.nickname)
        instance.profile.phone = profile_data.get(
            'phone', instance.profile.phone)
        instance.profile.parent_phone = profile_data.get(
            'parent_phone', instance.profile.parent_phone)
        instance.profile.gdpr = profile_data.get(
            'gdpr', instance.profile.gdpr)
        instance.profile.school = profile_data.get(
            'school', instance.profile.school)

        # User sa nikdy neupdatuje preto nie je potrebné volať instance.save()
        instance.profile.save()

        return instance


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', ]
