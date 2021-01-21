from rest_framework import viewsets
# from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from problem_database import models
from problem_database import serializers

# Filterset umoznuju pouzit URL v tvare profile/districts/?county=1
# Search filter umoznuju pouzit URL v tvare profile/schools/?search=Alej


class SeminarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Seminar.objects.all()
    serializer_class = serializers.SeminarSerializer


class ActivityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ActivityType.objects.all()
    serializer_class = serializers.ActivityTypeSerializer
    filterset_fields = ['seminar', ]


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer
    filterset_fields = ['activity_type', ]


class DifficultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Difficulty.objects.all()
    serializer_class = serializers.DifficultySerializer


class ProblemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ProblemType.objects.all()
    serializer_class = serializers.ProblemTypeSerializer


class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Problem.objects.all()
    serializer_class = serializers.ProblemSerializer
    filterset_fields = ['problem_type', ]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['problem']


class MediaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Media.objects.all()
    serializer_class = serializers.MediaSerializer
    filterset_fields = ['problem', ]


class ProblemActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ProblemActivity.objects.all()
    serializer_class = serializers.ProblemActivitySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ProblemTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ProblemTag.objects.all()
    serializer_class = serializers.ProblemTagSerializer
    filterset_fields = ['problem', 'tag']
