from django.urls import path

from .views import react_test

urlpatterns = [
    path('', react_test)
]
