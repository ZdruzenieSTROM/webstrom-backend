from rest_framework.routers import DefaultRouter
from base import views

app_name = 'base'


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'flat-page', views.FlatPageViewSet)


urlpatterns = [

]

urlpatterns += router.urls
