from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from problem_database.views import *

router = DefaultRouter()
router.register(r'seminars', SeminarViewSet)
router.register(r'activity_types', ActivityTypeViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'difficulty', DifficultyViewSet)
router.register(r'problems', ProblemViewSet)
router.register(r'media', MediaViewSet)
router.register(r'problem_activities', ProblemActivityViewSet)
router.register(r'problem_types', ProblemTypeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'problem_tags', ProblemTagViewSet)

app_name = "problem_database"

urlpatterns = [
    path('', include(router.urls)),
]