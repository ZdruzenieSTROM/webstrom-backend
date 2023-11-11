from django.urls import include, path

app_name = 'user'

urlpatterns = [path('', include('dj_rest_auth.urls')),
               path('registration/', include('dj_rest_auth.registration.urls')),
               ]
