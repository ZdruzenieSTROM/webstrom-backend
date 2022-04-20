from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from problem_database import views

router = DefaultRouter()
router.register(r'seminars', views.SeminarViewSet)
router.register(r'activity-types', views.ActivityTypeViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'difficulty', views.DifficultyViewSet)
router.register(r'problems', views.ProblemViewSet)
router.register(r'media', views.ProblemViewSet)
router.register(r'problem-activities', views.ProblemActivityViewSet)
router.register(r'problem-types', views.ProblemTypeViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'problem-tags', views.ProblemTagViewSet)

app_name = "problem_database"

urlpatterns = [
    path('', include(router.urls)),
]
