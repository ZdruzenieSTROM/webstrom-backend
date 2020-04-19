from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path, reverse_lazy

from user.views import (district_by_county, register, school_by_district,
                        send_verification_email, verify)

app_name = 'user'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('verify/<str:uidb64>/<str:token>/',
         verify, name='verify'),
    path('verify/send/', send_verification_email, name='verify-send'),

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

    path('district/<int:pk>/', district_by_county, name='filter_district'),
    path('school/<int:pk>/', school_by_district, name='filter_school'),
]
