from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from personal.models import County, District, Profile, School
from personal.serializers import (CountySerializer, DistrictSerializer,
                                  ProfileSerializer, SchoolSerializer)

# Filterset umoznuju pouzit URL v tvare profile/districts/?county=1
# Search filter umoznuju pouzit URL v tvare profile/schools/?search=Alej


class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """Kraje"""
    queryset = County.objects.all()
    serializer_class = CountySerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """Okresy"""
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filterset_fields = ['county', ]


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """Školy"""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filterset_fields = ['district', ]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'street']


class ProfileViewSet(viewsets.ModelViewSet):
    """Užívateľské profily"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filterset_fields = ['school', 'year_of_graduation', ]
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['first_name', 'last_name', 'nickname']

    # pylint: disable=inconsistent-return-statements
    @action(methods=['get', 'put'], detail=False, permission_classes=[IsAuthenticated])
    def myprofile(self, request):
        """Vráti profil prihláseného používateľa"""
        if request.method == 'GET':
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)

        if request.method == 'PUT':
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile, data=request.data)

            if serializer.is_valid():
                serializer.update(profile, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
