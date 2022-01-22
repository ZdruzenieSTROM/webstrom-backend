from rest_framework.routers import DefaultRouter

from cms import views

app_name = 'cms'


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'post', views.PostViewSet)
router.register(r'menu-item', views.MenuItemViewSet)
router.register(r'info-banner', views.InfoBannerViewSet)
router.register(r'message-template', views.MessageTemplateViewSet)


urlpatterns = [

]

urlpatterns += router.urls
