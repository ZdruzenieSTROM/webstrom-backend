from django.urls import path
from rest_framework.routers import DefaultRouter
from competition import views
from competition.views import (ArchiveView, LatestSeriesProblemsView,
                               SemesterInvitationsLatexView,
                               SemesterPublicationView,
                               SemesterRegistrationView,
                               SeriesProblemsView)

app_name = 'competition'

router = DefaultRouter()
router.register(r'problem', views.ProblemViewSet)
router.register(r'series', views.SeriesViewSet)
router.register(r'semester', views.SemesterViewSet)
router.register(r'solution', views.SolutionViewSet)


urlpatterns = [
    # Úlohy

    path('series/<int:pk>/problems', SeriesProblemsView.as_view(),
         name='series-problems-detail'),
    path('series/latest-problems', LatestSeriesProblemsView.as_view(),
         name='latest-series-problems'),

    # Výsledky

    #    path('series/<int:pk>/results', SeriesResultsView.as_view(),
    #         name='series-results'),
    #    path('series/<int:pk>/results/latex', SeriesResultsLatexView.as_view(),
    #         name='series-results-latex'),



    # Registrácia do semestra
    path('semester/<int:pk>/register/<path:cont>', SemesterRegistrationView.as_view(),
         name='semester-registration'),

    # Pozvánky
    path('semester/<int:pk>/invitations/<int:num_participants>/<int:num_substitutes>',
         SemesterInvitationsLatexView.as_view(),
         name='semester-invitations-latex'),
    # Publikácie
    path('semester/<int:pk>/publications',
         SemesterPublicationView.as_view(), name='semester-publications'),

    # Archív
    path('archive/', ArchiveView.as_view(),
         name='archive-view'),
]


urlpatterns += router.urls
