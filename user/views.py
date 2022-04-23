from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from allauth.account.views import ConfirmEmailView
from competition.forms import ProfileCreationForm, ProfileUpdateForm
from competition.models import Grade, Profile
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
# from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import DetailView
from personal.models import District, School
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import (CreateAPIView, GenericAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.forms import NameUpdateForm, UserCreationForm
from user.models import TokenModel, User
from user.serializers import (LoginSerializer, PasswordChangeSerializer,
                              RegisterSerializer, TokenSerializer,
                              UserDetailsSerializer, VerifyEmailSerializer)
from user.tokens import email_verification_token_generator

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


class LoginView(GenericAPIView):
    """Login"""
    #pylint: disable=attribute-defined-outside-init
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def login(self):
        self.user = self.serializer.validated_data['user']

        self.token = self.create_token(self.token_model, self.user)

        # Vytvorí django session.
        self.process_login()

    def get_response(self):
        serializer_class = TokenSerializer
        serializer = serializer_class(instance=self.token,
                                      context=self.get_serializer_context())

        response = Response(serializer.data, status=status.HTTP_200_OK)

        # Uloží token do webstrom-token cookie
        # Aktuálne sa webstrom-token cookie nastavuje na frontende.
        # Preto je ďalší riadok zakomentovaný.
        # response.set_cookie("webstrom-token", self.token,
        #                     expires=(timezone.now() + timezone.timedelta(weeks=4)))
        return response

    def post(self, request):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()

    def create_token(self, token_model, user):
        token, _ = token_model.objects.get_or_create(user=user)
        return token


class LogoutView(APIView):
    """Odhlásenie užívateľa"""
    #pylint: disable=unused-argument
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):

        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        # Zmaže django session.
        django_logout(request)

        response = Response(
            {"detail": "Úspešne odhlásený."},
            status=status.HTTP_200_OK
        )
        return response


class UserDetailsView(RetrieveUpdateAPIView):
    """Používateľ spolu s profilom"""
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class RegisterView(CreateAPIView):
    """Registrácia užívateľa"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny, ]
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({"detail": "Verifikačný email odoslaný."},
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)

        complete_signup(self.request._request, user,  # pylint: disable=protected-access
                        allauth_settings.EMAIL_VERIFICATION,  # pylint: disable=no-member
                        None)
        return user


class VerifyEmailView(APIView, ConfirmEmailView):
    """Emailová verifikácia užívateľa"""
    #pylint: disable=arguments-differ
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def get(self, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'detail': 'ok'}, status=status.HTTP_200_OK)


class PasswordChangeView(GenericAPIView):
    """Zmena hesla"""
    # pylint: disable=unused-argument
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Nové heslo bolo uložené"})


# Views ktoré neboli zatiaľ prepísané do restu.

@api_view(http_method_names=['POST'])
def register_api(request):
    # TODO: registrovanie
    pass


def register(request):
    if request.user.is_authenticated:
        return redirect('user:profile-update')

    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileCreationForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save(user)

            send_verification_email(user)
            messages.info(request, 'Odoslali sme ti overovací email')
            return redirect('user:login')

        if user_form.has_error('email', code='unique'):
            messages.error(
                request, render_to_string('user/messages/email_exists.html'))
    else:
        user_form = UserCreationForm()
        profile_form = ProfileCreationForm()

        profile_form.fields['district'].queryset = District.objects.none()
        profile_form.fields['school'].queryset = School.objects.none()

    return render(request, 'user/register.html',
                  {'user_form': user_form, 'profile_form': profile_form})


def send_verification_email(user):
    # Nie je mi úplne jasné, na čo je dobré user id zakódovať do base64,
    # ale používa to aj reset hesla tak prečo nie
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)

    message = render_to_string(
        'user/emails/email_verification.txt',
        {'uidb64': uidb64, 'token': token})
    html_message = render_to_string(
        'user/emails/email_verification.html',
        {'uidb64': uidb64, 'token': token})

    user.email_user('Overovací email', message, html_message=html_message)


def verify(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if email_verification_token_generator.check_token(user, token):
        user.verified_email = True
        user.save()

        messages.success(request, 'Tvoj email bol úspešne overený')
    else:
        messages.error(request, 'Tvoj email sa nepodarilo overiť')

    return redirect('/')


@login_required
def profile_update(request):
    user = request.user
    profile = request.user.profile

    if request.method == 'POST':
        user_form = NameUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            messages.info(request, 'Zmeny boli uložené.')
            return redirect('user:profile-detail', profile_form.save().pk)
    else:
        user_form = NameUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

        profile_form.fields['county'].initial = profile.school.district.county
        profile_form.fields['district'].initial = profile.school.district
        profile_form.fields['school_name'].initial = str(profile.school)
        profile_form.fields['grade'].initial = Grade.get_grade_by_year_of_graduation(
            year_of_graduation=profile.year_of_graduation).id

    return render(request, 'user/profile_update.html',
                  {'user_form': user_form, 'profile_form': profile_form})


class UserProfileView(DetailView):
    """Profil užívateľa"""
    template_name = 'user/profile_view.html'
    model = Profile
