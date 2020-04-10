
from django.urls import path, reverse_lazy

from competition.views import SemesterProblemsView

app_name = 'competition'

urlpatterns = [
    #path('register/', register, name='register'),
    #path('login/', LoginView.as_view(template_name='user/login.html'), name='login'),

    #path('district/<int:pk>/', district_by_county, name='filter_district'),
    path('semester/<int:pk>/', SemesterProblemsView.as_view(), name='semester_problem_views'),
]
