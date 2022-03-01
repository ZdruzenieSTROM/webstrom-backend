from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from cms.models import MenuItem, Post, InfoBanner, MessageTemplate
from cms.serializers import (
    MenuItemShortSerializer,
    PostSerializer,
    InfoBannerSerializer,
    MessageTemplateSerializer
)
from cms.permissions import PostPermission


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Položky menu"""
    queryset = MenuItem.objects.order_by('-priority')
    serializer_class = MenuItemShortSerializer

    @action(methods=['get'], detail=False, url_path=r'on-site/(?P<site_id>\d+)')
    def on_site(self, request, site_id):
        """Položky menu na stránke(na stránke Matik, Malynár ...)"""
        items = MenuItem.objects.filter(
            sites=site_id).order_by('-priority')
        serializer = MenuItemShortSerializer(items, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='on-current-site')
    def on_current_site(self, request):
        """Položky menu na aktuálnej stránke"""
        items = MenuItem.objects.filter(
            sites=request.site).order_by('-priority')
        serializer = MenuItemShortSerializer(items, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """Príspevky"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (PostPermission,)
    filterset_fields = ['sites', ]

    @action(detail=False)
    def visible(self, request):
        """Iba príspevky viditeľné pre užívateľov"""
        posts = self.filter_queryset(self.get_queryset()).visible()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class InfoBannerViewSet(viewsets.ModelViewSet):
    """Správy v čiernom info banneri"""
    serializer_class = InfoBannerSerializer
    queryset = InfoBanner.objects.visible()
    filterset_fields = ['event', 'page', 'series']


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """Templaty správ pre info banner/posty"""
    serializer_class = MessageTemplateSerializer
    queryset = MessageTemplate.objects.all()
