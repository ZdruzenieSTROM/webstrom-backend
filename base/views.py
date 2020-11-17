from django.contrib.flatpages.models import FlatPage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from base.serializers import FlatPageSerializer
# Create your views here.


class FlatPageViewSet(viewsets.ModelViewSet):
    """
    Obsluhuje API endpoint pre statické stránky
    """
    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]

    @action(methods=['get'], detail=False, url_path=r'by-url(?P<page_url>.+)')
    def by_url(self, request, page_url):
        page = FlatPage.objects.filter(url=page_url).first()
        serializer = FlatPageSerializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)
