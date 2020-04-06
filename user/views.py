from django.contrib import messages
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin

from user.forms import ProfileCreationForm, UserCreationForm
from user.models import County, District, School


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

            messages.success(
                request, 'Registrácia bola úspešná, môžes sa prihlásiť')

            return redirect(reverse('user:login'))
    else:
        user_form = UserCreationForm()
        profile_form = ProfileCreationForm()

    return render(request, 'user/register.html',
                  {'user_form': user_form, 'profile_form': profile_form})


def district_by_county(request, pk):
    county = get_object_or_404(County, pk=pk)
    queryset = District.objects.filter(county=county).values('pk', 'name')

    return JsonResponse(list(queryset), safe=False)


def school_by_district(request, pk):
    district = get_object_or_404(District, pk=pk)
    queryset = School.objects.filter(district=district)
    unknown_school = School.objects.filter(pk=0)

    return JsonResponse(list((queryset | unknown_school).values(
        'pk', 'name', 'street', 'city')), safe=False)


class VerificationSendView(RedirectView):
    # TODO: send email and redirect
    pass


class VerificationWaitingView(TemplateView):
    # TODO: email verification view
    # (email was send info and resend button)
    pass


class VerifyEmailView(RedirectView):
    # TODO: verify email by 'key', login and redirect
    pass
