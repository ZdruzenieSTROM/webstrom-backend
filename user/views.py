from competition.forms import ProfileCreationForm, ProfileUpdateForm
from competition.models import Grade, Profile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import DetailView

from rest_framework.decorators import api_view

from profile.models import District, School

from user.forms import NameUpdateForm, UserCreationForm
from user.models import User
from user.tokens import email_verification_token_generator


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
        elif user_form.has_error('email', code='unique'):
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
    template_name = 'user/profile_view.html'
    model = Profile
