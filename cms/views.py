

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from cms.models import InfoBanner, Logo, MenuItem, MessageTemplate, Post
from cms.permissions import PostPermission
from cms.serializers import (InfoBannerSerializer, LogoSerializer,
                             MenuItemShortSerializer,
                             MessageTemplateSerializer, PostSerializer)


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Položky menu"""
    queryset = MenuItem.objects.order_by('-priority')
    serializer_class = MenuItemShortSerializer

    def filter_(self, queryset, filter_by: str | None):
        if filter_by == 'menu':
            queryset = queryset.filter(in_menu=True)
        if filter_by == 'footer':
            queryset = queryset.filter(in_footer=True)
        return queryset

    @action(methods=['get'], detail=False, url_path=r'on-site/(?P<site_id>\d+)')
    def on_site(self, request: Request, site_id):
        """Položky menu na stránke(na stránke Matik, Malynár ...)"""
        filter_by = request.query_params.get('type')
        queryset = self.get_queryset().filter(
            sites=site_id)
        items = self.filter_(queryset, filter_by)
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


class LogoViewSet(viewsets.ReadOnlyModelViewSet):
    """Logá"""
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer


class InfoBannerViewSet(viewsets.ModelViewSet):
    """Správy v čiernom info banneri"""
    serializer_class = InfoBannerSerializer
    queryset = InfoBanner.objects.visible()
    filterset_fields = ['event', 'page', 'series']


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """Templaty správ pre info banner/posty"""
    serializer_class = MessageTemplateSerializer
    queryset = MessageTemplate.objects.all()
