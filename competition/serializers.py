from rest_framework import serializers
from competition import models


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Problem
        fields = '__all__'


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
     class Meta:
        model = models.Semester
        fields = '__all__'
