"""
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from user.views import *

app_name = 'user'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='sign_up'),
    path('verification/', VerificationSendView.as_view(), name='verification_send'),
    path('verification/', VerificationWaitingView.as_view(), name='verification_waiting'),
    path('verify/<str:key>/', VerifyEmailView.as_view(), name='verify'),
    path('login/', LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
