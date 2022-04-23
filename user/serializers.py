from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from django_typomatic import ts_interface
from rest_framework import exceptions, serializers

from competition.models import Grade
from personal.models import Profile
from personal.serializers import ProfileCreateSerializer
from user.models import TokenModel, User
from webstrom.settings import EMAIL_ALERT, EMAIL_NO_REPLY


@ts_interface(context='user')
class LoginSerializer(serializers.Serializer):
    # pylint: disable=W0223
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
        # pylint: disable=E1101
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

@ts_interface(context='user')
class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer pre Token model.
    """

    class Meta:
        model = TokenModel
        fields = ('key',)

@ts_interface(context='user')
class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer pre User model spolu s Profile modelom
    """

    profile = ProfileCreateSerializer(label='')

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
            Profile.objects.create(user=instance, **profile_data)

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
        instance.profile.year_of_graduation = profile_data.get(
            'year_of_graduation', instance.profile.year_of_graduation)

        # User sa nikdy neupdatuje preto nie je potrebné volať instance.save()
        instance.profile.save()

        return instance


@ts_interface(context='user')
class RegisterSerializer(serializers.Serializer):
    # pylint: disable=w0223
    # pylint: disable=w0221
    # pylint: disable=w0201
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    profile = ProfileCreateSerializer(label="")
    new_school_description = serializers.CharField(
        max_length=200, allow_blank=True)

    OTHER_SCHOOL_CODE = 0

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                "Používateľ s danou emailovou adresou už existuje.")
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate_profile(self, profile):
        '''
        check ci je gdpr zaskrtnute
        '''
        if not profile['gdpr']:
            raise serializers.ValidationError(
                'Musíš podvrdiť, že si si vedomý spracovania osobných údajov.')
        return profile

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Zadané heslá sa nezhodujú.")

        # ak je zadana skola "ina skola", musi byt nejaky description skoly
        if (attrs['profile']['school'].code == self.OTHER_SCHOOL_CODE and
                len(attrs['new_school_description']) == 0):
            raise serializers.ValidationError(
                'Musíš zadať popis tvojej školy.')

        return attrs

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        profile_data = self.validated_data['profile']
        grade = Grade.objects.get(pk=profile_data['grade'])

        Profile.objects.create(user=user,
                               first_name=profile_data['first_name'],
                               last_name=profile_data['last_name'],
                               nickname=profile_data['nickname'],
                               school=profile_data['school'],
                               year_of_graduation=grade.get_year_of_graduation_by_date(),
                               phone=profile_data['phone'],
                               parent_phone=profile_data['parent_phone'],
                               gdpr=profile_data['gdpr'])

        self.handle_other_school(profile_data['school'])
        setup_user_email(request, user, [])

        return user

    def handle_other_school(self, school):
        '''
        Ak je zadana skola "ina skola" tak posle o tom mail.
        '''
        if school.code == self.OTHER_SCHOOL_CODE:
            email = self.validated_data['email']
            name = self.validated_data['profile']['first_name']\
                + self.validated_data['profile']['last_name']
            school_info = self.validated_data['new_school_description']
            send_mail(
                'Žiadosť o pridanie novej školy',
                f'''Na webe sa zaregistroval nový používateľ a nenašiel svoju školu.
                Email: {email}
                Meno: {name}
                Škola: {school_info}

                Prosím doplňte školu a priraďte mu ju.
                ''',
                EMAIL_NO_REPLY,
                [EMAIL_ALERT]
            )

@ts_interface(context='user')
class VerifyEmailSerializer(serializers.Serializer):
    # pylint: disable=w0223
    key = serializers.CharField()

@ts_interface(context='user')
class PasswordChangeSerializer(serializers.Serializer):
    # pylint: disable=w0223
    # pylint: disable=w0221
    # pylint: disable=w0201
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = True
        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            err_msg = "Staré heslo bolo zadané nesprávne."
            raise serializers.ValidationError(err_msg)
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()

@ts_interface(context='user')
class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', ]
