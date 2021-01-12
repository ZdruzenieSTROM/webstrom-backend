from django.shortcuts import render

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from problem_database.models import *
from problem_database.serializers import *

# Filterset umoznuju pouzit URL v tvare profile/districts/?county=1
# Search filter umoznuju pouzit URL v tvare profile/schools/?search=Alej


class SeminarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer

    def create(self, request, *args, **kwargs):
        many = True if isinstance(request.data, list) else False
        serializer = SeminarSerializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class ActivityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer
    filterset_fields = ['seminar',]
    

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filterset_fields = ['activity_type',]
    

class DifficultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Difficulty.objects.all()
    serializer_class = DifficultySerializer
    

class ProblemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProblemType.objects.all()
    serializer_class = ProblemTypeSerializer    


class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filterset_fields = ['problem_type',]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['problem']

    def create(self, request, *args, **kwargs):
        many = True if isinstance(request.data, list) else False
        serializer = ProblemSerializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class MediaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    filterset_fields = ['problem',]
    

class ProblemActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProblemActivity.objects.all()
    serializer_class = ProblemActivitySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    

class ProblemTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagSerializer
    filterset_fields = ['problem','tag']