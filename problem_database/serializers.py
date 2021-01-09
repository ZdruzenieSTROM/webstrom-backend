from rest_framework import serializers

from problem_database.models import *


class SeminarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seminar
        fields = '__all__'


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Difficulty
        fields = '__all__'


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = '__all__'


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class ProblemActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemActivity
        fields = '__all__'


class ProblemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemType
        fields = '__all__'


class ProblemProblemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemProblemType
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ProblemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag
        fields = '__all__'