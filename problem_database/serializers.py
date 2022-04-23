from django_typomatic import ts_interface
from rest_framework import serializers

from problem_database import models


@ts_interface(context='problem_database')
class SeminarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seminar
        fields = '__all__'

@ts_interface(context='problem_database')
class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActivityType
        fields = '__all__'

@ts_interface(context='problem_database')
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields = '__all__'

@ts_interface(context='problem_database')
class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Difficulty
        fields = '__all__'

@ts_interface(context='problem_database')
class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Problem
        fields = '__all__'

@ts_interface(context='problem_database')
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Media
        fields = '__all__'

@ts_interface(context='problem_database')
class ProblemActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProblemActivity
        fields = '__all__'

@ts_interface(context='problem_database')
class ProblemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProblemType
        fields = '__all__'

@ts_interface(context='problem_database')
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'

@ts_interface(context='problem_database')
class ProblemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProblemTag
        fields = '__all__'
