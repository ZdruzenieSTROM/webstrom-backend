from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, status, viewsets
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


class SchoolViewSet(viewsets.ModelViewSet):
    """Školy"""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filterset_fields = ['district', 'district__county']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'street', 'city']

    def destroy(self, request, *args, **kwargs):
        """Zmazanie školy"""
        instance = self.get_object()
        if Profile.objects.filter(school=instance).exists():
            raise exceptions.ValidationError(
                detail='Nie je možné zmazať školu, ktorá má priradených užívateľov.')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ModelViewSet):
    """Užívateľské profily"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filterset_fields = ['school', 'year_of_graduation', ]
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['first_name', 'last_name']

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

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def mypermissions(self, request):
        is_staff = request.user.is_staff
        is_superuser = request.user.is_superuser
        competition_set = set()
        for group in request.user.groups.all():
            for competition in group.competition_permissions.all():
                competition_set.add(competition.pk)
        return Response({
            'is_staff': is_staff,
            'is_superuser': is_superuser,
            'competition_permissions': competition_set,
        }, status=status.HTTP_200_OK)
