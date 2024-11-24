from django.urls import path

from base import views

app_name = 'base'

urlpatterns = [
    path(r'api-docs/', views.SwaggerSchemaView.as_view(), name='api-docs'),
]
