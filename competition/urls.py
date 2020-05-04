from django.urls import path

from competition.views import (ArchiveView, LatestSemesterView,
                               SemesterDetailView, SemesterProblemsView,
                               SemesterResultsLatexView, SemesterResultsView,
                               SeriesProblemsView, SeriesResultsLatexView,
                               SeriesResultsView)

app_name = 'competition'

urlpatterns = [
    path('semester/latest/', LatestSemesterView.as_view(),
         name='latest-semester-view'),
    path('semester/<int:pk>/problems/', SemesterProblemsView.as_view(),
         name='semester-problems-detail'),
    path('semester/<int:pk>/', SemesterDetailView.as_view(),
         name='semester-detail'),

    path('series/<int:pk>/', SeriesProblemsView.as_view(),
         name='series-problems-detail'),

    path('archive/', ArchiveView.as_view(),
         name='archive-view'),

    path('semester/<int:pk>/results', SemesterResultsView.as_view(),
         name='semester-results'),

    path('semester/<int:pk>/results/latex', SemesterResultsLatexView.as_view(),
         name='semester-results-latex'),

    path('series/<int:pk>/results', SeriesResultsView.as_view(),
         name='semester-results'),

    path('series/<int:pk>/results/latex', SeriesResultsLatexView.as_view(),
         name='semester-results-latex'),
]
