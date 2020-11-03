from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter

from .views import CountyViewSet, DistrictViewSet, ProfileViewSet, SchoolViewSet

router = DefaultRouter()
router.register(r'counties', CountyViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'schools', SchoolViewSet)
router.register(r'profiles', ProfileViewSet)

app_name = "profile"

urlpatterns = [
    path('', include(router.urls)),
]
