from rest_framework import viewsets, exceptions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from cms.models import InfoBanner, MenuItem, MessageTemplate, Post, Logo
from cms.permissions import PostPermission
from cms.serializers import (InfoBannerSerializer, MenuItemShortSerializer,
                             MessageTemplateSerializer, PostSerializer, LogoSerializer)


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


class LogoViewSet(viewsets.ModelViewSet):
    """Publikácie(výsledky, brožúrky, časopisy, ...)"""
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer
    permission_classes = (PostPermission,)

    def perform_create(self, serializer):
        '''
        Vola sa pri vytvarani objektu,
        checkuju sa tu permissions, ci user vie vytvorit publication v danom evente
        '''
        event = serializer.validated_data['event']
        if event.can_user_modify(self.request.user):
            serializer.save()
        else:
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

    @action(methods=['post'], detail=False, url_path='upload')
    def check_file(self, request):
        if 'file' not in request.data:
            raise exceptions.ParseError(detail='Request neobsahoval súbor')

        return Response(status=status.HTTP_201_CREATED)



class InfoBannerViewSet(viewsets.ModelViewSet):
    """Správy v čiernom info banneri"""
    serializer_class = InfoBannerSerializer
    queryset = InfoBanner.objects.visible()
    filterset_fields = ['event', 'page', 'series']


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """Templaty správ pre info banner/posty"""
    serializer_class = MessageTemplateSerializer
    queryset = MessageTemplate.objects.all()
