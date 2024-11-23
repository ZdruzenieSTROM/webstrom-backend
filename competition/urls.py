from rest_framework.routers import DefaultRouter

from competition import views

app_name = 'competition'

router = DefaultRouter()
router.register(r'competition', views.CompetitionViewSet)
router.register(r'problem', views.ProblemViewSet)
router.register(r'series', views.SeriesViewSet)
router.register(r'semester', views.SemesterViewSet)
router.register(r'semester-list', views.SemesterListViewSet,
                basename='semester-list')
router.register(r'solution', views.SolutionViewSet)
router.register(r'event', views.EventViewSet)
router.register(r'publication', views.PublicationViewSet)
router.register(r'comment', views.CommentViewSet)
router.register(r'late-tag', views.LateTagViewSet)
router.register(r'grade', views.GradeViewSet)
router.register(r'problem-administration',
                views.ProblemAdministrationViewSet, basename="problem-administration")
router.register(r'event-registration', views.EventRegistrationViewSet)
router.register(r'competition-type', views.CompetitionTypeViewSet)
router.register(r'publication-type', views.PublicationTypeViewSet)

urlpatterns = []

urlpatterns += router.urls
