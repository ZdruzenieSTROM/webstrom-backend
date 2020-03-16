from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView

from user.models import User
from user.forms import *


class SignupView(FormView):
    # TODO: sign up view
    pass


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
