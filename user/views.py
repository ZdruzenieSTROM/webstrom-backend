from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import SingleObjectMixin

from user.forms import ProfileCreationForm, UserCreationForm
from user.models import County, District, School


def signup(request):
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

    return render(request, 'user/signup.html',
                  {'user_form': user_form, 'profile_form': profile_form})


class FilterDistrictView(TemplateView, SingleObjectMixin):
    model = County

    template_name = 'user/district_options.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['districts'] = District.objects.filter(
            county=self.object)

        return context


class FilterSchoolView(TemplateView, SingleObjectMixin):
    model = District

    template_name = 'user/school_options.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['schools'] = School.objects.filter(
            district=self.object) | School.objects.filter(pk=0)

        return context


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
