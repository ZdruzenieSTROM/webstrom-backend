
from django.urls import path, reverse_lazy

from competition.views import SemesterProblemsView

app_name = 'competition'

urlpatterns = [
    path('semester/<int:pk>/', SemesterProblemsView.as_view(), name='semester-problems-detail'),
]
