from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from user.forms import ProfileCreationForm, UserCreationForm
from user.models import County, District, School, User
from user.tokens import email_verification_token


def register(request):
    # TODO: presmerovať prihlásených preč, asi na zmenu profilu
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileCreationForm(request.POST)

        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()

        if user_form_valid and profile_form_valid:
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)

            return redirect('user:verify-send')
    else:
        user_form = UserCreationForm()
        profile_form = ProfileCreationForm()

        # profile_form.fields['district'].queryset = District.objects.none()
        # profile_form.fields['school'].queryset = School.objects.none()

    return render(request, 'user/register.html',
                  {'user_form': user_form, 'profile_form': profile_form})


def send_verification_email(request):
    if not request.user.is_authenticated:
        messages.error(
            request, 'Na poslanie overovacieho emailu sa musíš prihlásiť')

    elif request.user.verified_email:
        messages.error(
            request, 'Tvoj email už je overený')
    else:
        message = render_to_string('user/email/email_verification.html', {
            'uidb64': urlsafe_base64_encode(force_bytes(request.user.pk)),
            'token': email_verification_token.make_token(request.user)
        })

        send_mail('Overovací email', message,
                  'web@strom.sk', [request.user.email])

        messages.success(request, 'Odoslali sme ti overovací email')

    return redirect('/')


def verify(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.verified_email = True
        user.save()

        messages.success(request, 'Tvoj email bol úspešne overený')
    else:
        messages.error(request, 'Tvoj email sa nepodarilo overiť')

    return redirect('/')


def district_by_county(request, pk):
    county = get_object_or_404(County, pk=pk)
    queryset = District.objects.filter(county=county).values('pk', 'name')

    return JsonResponse(list(queryset), safe=False)


def school_by_district(request, pk):
    district = get_object_or_404(District, pk=pk)
    queryset = School.objects.filter(
        district=district, include_unspecified=True)

    values = [{'pk': school.pk, 'name': str(school)} for school in queryset]

    return JsonResponse(list(values), safe=False)
