from rest_framework.routers import DefaultRouter

from .views import (FileUploadViewSet, FlatPageViewSet, GalleryViewSet,
                    InfoBannerViewSet, LogoViewSet, MenuItemViewSet,
                    MessageTemplateViewSet, PostViewSet)

router = DefaultRouter()

router.register('post', PostViewSet)
router.register('menu-item', MenuItemViewSet)
router.register('info-banner', InfoBannerViewSet)
router.register('message-template', MessageTemplateViewSet)
router.register('logo', LogoViewSet)
router.register('uploads', FileUploadViewSet)
router.register('flat-page', FlatPageViewSet)
router.register('gallery', GalleryViewSet)

app_name = 'cms'

urlpatterns = router.urls
