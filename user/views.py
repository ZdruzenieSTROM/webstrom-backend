from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.detail import DetailView


from user.forms import ProfileCreationForm, UserCreationForm, ProfileUpdateForm
from user.models import County, District, School, User, Profile
from user.tokens import email_verification_token_generator


def register(request):
    # TODO: presmerovať prihlásených preč, asi na zmenu profilu
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileCreationForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

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
    message = render_to_string('user/emails/email_verification.html', {
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': email_verification_token_generator.make_token(user)})

    send_mail('Overovací email', message, 'web@strom.sk', [user.email, ])


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


def district_by_county(request, pk):
    county = get_object_or_404(County, pk=pk)
    queryset = District.objects.filter(county=county).values('pk', 'name')

    return JsonResponse(list(queryset), safe=False)


def school_by_district(request, pk):
    district = get_object_or_404(District, pk=pk)
    queryset = School.objects.filter(district=district)

    values = [{'value': school.pk, 'label': str(school)}
              for school in queryset]

    return JsonResponse(values, safe=False)


class UserProfileView(DetailView):
    template_name = 'user/profile_view.html'
    model = Profile
    context_object_name = 'profile'


def profile_update(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)

        if form.is_valid():
            upd_profile = form.save(commit=False)
            upd_profile.user = profile.user
            upd_profile.save()

            messages.info(request, 'Zmeny boli uložené.')
            return redirect('user:profile-detail', upd_profile.id)
    else:
        form = ProfileUpdateForm(instance=profile)

        form.fields['county'].initial = profile.school.district.county
        form.fields['district'].initial = profile.school.district
        form.fields['school_name'].initial = str(profile.school)
        form.fields['grade'].initial = profile.grade().id

    return render(request, 'user/profile_update.html', {'form': form})
