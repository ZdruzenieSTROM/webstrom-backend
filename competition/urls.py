from django.urls import path

from competition.views import (
    LatestSemesterView,
    SemesterProblemsView,
    SeriesProblemsView,
    ArchiveView,
    SemesterDetailView
)

app_name = 'competition'

urlpatterns = [
    path('semester/<int:pk>/problems', SemesterProblemsView.as_view(),
         name='semester-problems-detail'),
    path('semester-last', LatestSemesterView.as_view(),
         name='latest-semester-view'),
    path('series/<int:pk>/', SeriesProblemsView.as_view(),
         name='series-problems-detail'),
    path('archive', ArchiveView.as_view(),
         name='archive-view'),
    path('semester/<int:pk>/', SemesterDetailView.as_view(),
         name='semester-detail'),
]
