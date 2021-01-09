from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from problem_database.models import *
from problem_database.serializers import *

# Filterset umoznuju pouzit URL v tvare profile/districts/?county=1
# Search filter umoznuju pouzit URL v tvare profile/schools/?search=Alej


class SeminarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = [IsAdminUser]


class ActivityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer
    filterset_fields = ['seminar', ]
    permission_classes = [IsAdminUser]


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filterset_fields = ['activity_type', ]
    permission_classes = [IsAdminUser]


class DifficultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Difficulty.objects.all()
    serializer_class = DifficultySerializer
    permission_classes = [IsAdminUser]


class ProblemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProblemType.objects.all()
    serializer_class = ProblemTypeSerializer
    permission_classes = [IsAdminUser]


class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filterset_fields = ['problem_type', ]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['problem']
    permission_classes = [IsAdminUser]


class MediaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    filterset_fields = ['problem', ]
    permission_classes = [IsAdminUser]


class ProblemActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProblemActivity.objects.all()
    serializer_class = ProblemActivitySerializer
    permission_classes = [IsAdminUser]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]


class ProblemTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagSerializer
    filterset_fields = ['problem', 'tag']
    permission_classes = [IsAdminUser]
