from django.shortcuts import redirect, render, reverse
from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView
from django.contrib import messages

from user.forms import ProfileCreationForm, UserCreationForm


def signup(request):
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
