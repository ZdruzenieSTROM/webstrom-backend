from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

api_urlpatterns = [
    path('user/', include('user.urls')),
    path('competition/', include('competition.urls')),
    path('cms/', include('cms.urls')),
    path('personal/', include('personal.urls')),
    path('base/', include('base.urls')),
    path('protected/', include('downloads.urls')),
]

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('django-admin/', admin.site.urls),
    path(settings.API_PREFIX, include(api_urlpatterns)),
]

# Pri vývoji servuj media files priamo z djanga
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
