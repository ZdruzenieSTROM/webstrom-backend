from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from rest_framework import permissions, renderers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from cms.models import Post
from cms.serializers import PostSerializer
from cms.permissions import UserPermission


class PostViewSet(viewsets.ModelViewSet):
    """
    Obsluhuje API endpoint pre Posty
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (UserPermission,)

    @action(detail=False)
    def visible(self, request, *args, **kwargs):
        posts = Post.objects.all()
        posts = [p for p in posts if p.is_visible]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def retrieve_visible(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=pk).first()
        if not post.is_visible:
            raise PermissionDenied()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
