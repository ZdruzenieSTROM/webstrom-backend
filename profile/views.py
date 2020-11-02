from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from .models import County, District, Profile, School
from .serializers import CountySerializer, DistrictSerializer, ProfileSerializer, SchoolSerializer

# Filterset umoznuju pouzit URL v tvare profile/districts/?county=1
# Search filter umoznuju pouzit URL v tvare profile/schools/?search=Alej


class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filterset_fields = ['county', ]


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filterset_fields = ['district', ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'street']


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filterset_fields = ['school', 'year_of_graduation', ]
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'nickname']
