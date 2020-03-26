from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView)
from django.urls import path, reverse_lazy

from user.views import (SignupView, VerificationSendView,
                        VerificationWaitingView, VerifyEmailView)

app_name = 'user'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='sign_up'),
    path('login/', LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('verification/', VerificationSendView.as_view(), name='verification_send'),
    path('verification/', VerificationWaitingView.as_view(),
         name='verification_waiting'),
    path('verify/<str:key>/', VerifyEmailView.as_view(), name='verify'),

    path('password-reset/',
         PasswordResetView.as_view(
             template_name='user/password_reset.html',
             success_url=reverse_lazy('user:password_reset_done'),
             email_template_name='emails/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='user/password_reset_confirm.html',
             success_url=reverse_lazy('user:password_reset_complete'),
         ),
         name='password_reset_confirm'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(
             template_name='user/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(
             template_name='user/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('password-change/',
         PasswordChangeView.as_view(
             template_name='user/password_change.html',
             success_url=reverse_lazy('user:password_change_done'),
         ),
         name='password_change'),
    path('password-change/done/',
         PasswordChangeDoneView.as_view(
             template_name='user/password_change_done.html'
         ),
         name='password_change_done'),
]
