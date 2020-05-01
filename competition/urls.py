from django.urls import path

from competition.views import (ArchiveView, LatestSemesterView,
                               SemesterDetailView, SemesterProblemsView,
                               SeriesProblemsView, ResultsView)

app_name = 'competition'

urlpatterns = [
    path('semester/latest/', LatestSemesterView.as_view(),
         name='latest-semester-view'),

    #tento view by sa nemal pouzivat, namiesto neho je seriesProblemsView
    #path('semester/<int:pk>/problems/', SemesterProblemsView.as_view(),
    #     name='semester-problems-detail'),

    path('semester/<int:pk>/', SemesterDetailView.as_view(),
         name='semester-detail'),

    path('series/<int:pk>/problems', SeriesProblemsView.as_view(),
         name='series-problems-detail'),
    
    path('series/<int:pk>/results', ResultsView.as_view(),
         name='series-results-detail'),

    path('archive/', ArchiveView.as_view(),
         name='archive-view'),
]
