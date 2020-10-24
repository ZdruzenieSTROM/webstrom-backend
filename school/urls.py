from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter

from .views import CountyViewSet, DistrictViewSet, SchoolViewSet

router = DefaultRouter()
router.register(r'counties', CountyViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'schools', SchoolViewSet)

app_name = "school"

urlpatterns = [
    path('', include(router.urls)),
]
