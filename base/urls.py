from django.urls import path
from rest_framework.routers import DefaultRouter

from base import views

app_name = 'base'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'flat-page', views.FlatPageViewSet)


urlpatterns = [
    path(r'api-docs/', views.SwaggerSchemaView.as_view(), name='api-docs')
]

urlpatterns += router.urls
