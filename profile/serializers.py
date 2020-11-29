from rest_framework import serializers

from .models import County, District, Profile, School


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class SchoolShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        exclude = ['email', 'district']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    first_name = serializers.CharField(
        source='user.first_name', read_only=False)
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')


class ProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname']

    first_name = serializers.CharField(
        source='user.first_name', read_only=False)
    last_name = serializers.CharField(source='user.last_name')


class ProfileMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname', 'email']

    first_name = serializers.CharField(
        source='user.first_name', read_only=False)
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
