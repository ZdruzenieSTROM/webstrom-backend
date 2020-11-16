from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('competition/', include('competition.urls')),
    path('cms/', include('cms.urls')),
    path('profile/', include('profile.urls')),
    path('base/', include('base.urls')),
]

# Pri vývoji servuj media files priamo z djanga
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
