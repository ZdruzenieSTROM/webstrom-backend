from rest_framework import serializers

from personal.serializers import ProfileShortSerializer, SchoolShortSerializer
from competition import models


class UnspecifiedPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UnspecifiedPublication
        fields = '__all__'


class SemesterPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SemesterPublication
        fields = '__all__'


class RegistrationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegistrationLink
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    unspecifiedpublication_set = UnspecifiedPublicationSerializer(many=True)
    registration_links = RegistrationLinkSerializer(many=True)

    class Meta:
        model = models.Event
        fields = '__all__'


class CompetitionSerializer(serializers.ModelSerializer):
    event_set = EventSerializer(many=True)

    class Meta:
        model = models.Competition
        fields = '__all__'


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventRegistration
        fields = ['school', 'grade', 'profile']
    school = SchoolShortSerializer(many=False)
    grade = serializers.SlugRelatedField(
        slug_field='tag', many=False, read_only=True)
    profile = ProfileShortSerializer(many=False)


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Problem
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vote
        fields = '__all__'


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Solution
        fields = '__all__'
    votes = VoteSerializer(many=True)


# class ProblemStatsSerializer(serializers.Serializer):
#    historgram = HistrogramItemSerializer(many=True)
#    num_solutions = serializers.IntegerField()
#   mean = serializers.FloatField()
#

class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Series
        exclude = ['sum_method']


class SeriesWithProblemsSerializer(serializers.ModelSerializer):
    problems = ProblemSerializer(many=True)

    class Meta:
        model = models.Series
        exclude = ['sum_method']

    def create(self, validated_data):
        problem_data = validated_data.pop('problems')
        series = models.Series.objects.create(**validated_data)
        for data in problem_data:
            models.Problem.objects.create(series=series, **data)
        return series


class SemesterSerializer(serializers.ModelSerializer):
    series_set = SeriesSerializer(many=True)

    class Meta:
        model = models.Semester
        fields = '__all__'

    def create(self, validated_data):
        series_data = validated_data.pop('series_set')
        semester = models.Semester.objects.create(**validated_data)
        for series in series_data:
           models.Series.objects.create(semester=semester,**series)
        return semester

class SemesterWithProblemsSerializer(serializers.ModelSerializer):
    series_set = SeriesWithProblemsSerializer(many=True)
    semesterpublication_set = SemesterPublicationSerializer(many=True)
    unspecifiedpublication_set = UnspecifiedPublicationSerializer(many=True)

    class Meta:
        model = models.Semester
        fields = '__all__'
   
    def create(self, validated_data):
        series_data = validated_data.pop('series_set')
        semesterpublication_data = validated_data.pop('semesterpublication_set')
        unspecifiedpublication_data = validated_data.pop('unspecifiedpublication_set')
        semester = models.Semester.objects.create(**validated_data)
        for series in series_data:
           models.Series.objects.create(semester=semester,**series)
        for semesterpublication in semesterpublication_data:
           models.SemesterPublication.objects.create(semester=semester,**semesterpublication)
        for unspecifiedpublication in unspecifiedpublication_data:
           models.UnspecifiedPublication.objects.create(event=semester,**unspecifiedpublication)
        return semester