from django.conf import settings
from django.urls import path

from base import views

app_name = 'base'

if settings.DEBUG:
    urlpatterns = [
        path(r'api-docs/', views.SwaggerSchemaView.as_view(), name='api-docs'),
    ]
else:
    urlpatterns = []
