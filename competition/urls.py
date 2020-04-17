from django.urls import path

from competition.views import LatestSemesterView, SemesterProblemsView

app_name = 'competition'

urlpatterns = [
    path('semester/<int:pk>/', SemesterProblemsView.as_view(),
         name='semester-problems-detail'),
    path('semester-last', LatestSemesterView.as_view(),
         name='latest-semester-view')
]
