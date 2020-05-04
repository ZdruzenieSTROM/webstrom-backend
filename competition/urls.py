from django.urls import path

from competition.views import (ArchiveView, LatestSemesterView,
                               SemesterDetailView, SemesterProblemsView,
                               SeriesProblemsView, ResultsView, LatestSeriesProblemsView)

app_name = 'competition'

urlpatterns = [
     path('series/<int:pk>/problems', SeriesProblemsView.as_view(),
         name='series-problems-detail'),
    
     path('series/latest-problems', LatestSeriesProblemsView.as_view(),
         name='latest-series-problems'),

     path('series/<int:pk>/results', ResultsView.as_view(),
         name='series-results-detail'),

    path('archive/', ArchiveView.as_view(),
         name='archive-view'),
]
