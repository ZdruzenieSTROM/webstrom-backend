from django.contrib.flatpages.models import FlatPage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, IsAdminUser
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers
from base.serializers import FlatPageSerializer


# Create your views here.


class FlatPageViewSet(viewsets.ModelViewSet):
    """
    Statické stránky
    """
    queryset = FlatPage.objects.all()
    serializer_class = FlatPageSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]

    @action(methods=['get'], detail=False, url_path=r'by-url/(?P<page_url>.+)')
    def by_url(self, request, page_url):
        """Vráti statickú stránku podľa jej url"""
        page = FlatPage.objects.filter(url=page_url).first()
        serializer = FlatPageSerializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SwaggerSchemaView(APIView):
    """Prehľad API pointov"""
    permission_classes = [IsAdminUser]
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = SchemaGenerator()
        schema = generator.get_schema(request=request)
        return Response(schema)
