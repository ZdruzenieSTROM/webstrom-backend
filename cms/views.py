from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from cms.models import MenuItem, Post
from cms.serializers import MenuItemShortSerializer, PostSerializer
from cms.permissions import PostPermission


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Obsluhuje API endpoint pre MenuItems
    """
    queryset = MenuItem.objects.order_by('-priority')
    serializer_class = MenuItemShortSerializer

    @action(methods=['get'], detail=False, url_path=r'on-site/(?P<site_id>\d+)')
    def on_site(self, request, site_id):
        items = MenuItem.objects.filter(
            sites=site_id).order_by('-priority')
        serializer = MenuItemShortSerializer(items, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='on-current-site')
    def on_current_site(self, request):
        items = MenuItem.objects.filter(
            sites=request.site).order_by('-priority')
        serializer = MenuItemShortSerializer(items, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """
    Obsluhuje API endpoint pre Príspevky
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (PostPermission,)

    @action(detail=False)
    def visible(self, request):
        posts = Post.objects.all()
        posts = [p for p in posts if p.is_visible]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
