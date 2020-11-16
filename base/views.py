from django.contrib.flatpages.models import FlatPage
from rest_framework import viewsets
from base.serializers import FlatPageSerializer
# Create your views here.


class FlatPageViewSet(viewsets.ModelViewSet):
    """
    Obsluhuje API endpoint pre statické stránky
    """
    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
