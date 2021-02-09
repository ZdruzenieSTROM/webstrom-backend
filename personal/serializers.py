from rest_framework import serializers

from personal.models import County, District, Profile, School
from competition.models import Grade

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
    grade = serializers.SerializerMethodField('get_grade')

    def get_grade(self, profile):
        return Grade.get_grade_by_year_of_graduation(
            year_of_graduation=profile.year_of_graduation,
            date=None
        )

    class Meta:
        model = Profile
        fields = ['first_name','last_name','nickname','school','year_of_graduation','phone','parent_phone','gdpr','grade']
        read_only_fields = ['first_name', 'last_name', 'email']
        email = serializers.EmailField(source='user.email')

    def update(self, profile, validated_data):
        for attr, value in validated_data.items():
            setattr(profile, attr, value)
        setattr(
            profile, 
            'year_of_graduation', 
            Grade.get_year_of_graduation_by_date(
                validated_data['grade'],
                date=None
            )
        )
        profile.save()
        return profile

    def create(self, validated_data):
        grade = Grade.objects.create(validated_data['grade'])
        return Profile.objects.create(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            nickname = validated_data['nickname'],
            school = validated_data['school'],
            year_of_graduation = grade.get_year_of_graduation_by_date(),
            phone = validated_data['phone'],
            parent_phone = validated_data['parent_phone'],
            gdpr = validated_data['gdpr']
        )


class ProfileCreateSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField('get_grade')

    def get_grade(self, profile):
        return Grade.get_grade_by_year_of_graduation(
            year_of_graduation=profile.year_of_graduation,
            date=None
        )

    class Meta:
        model = Profile
        fields = ['first_name','last_name','nickname','school','year_of_graduation','phone','parent_phone','gdpr','grade']

    def update(self, profile, validated_data):
        for attr, value in validated_data.items():
            setattr(profile, attr, value)
        setattr(
            profile, 
            'year_of_graduation', 
            Grade.get_year_of_graduation_by_date(
                validated_data['grade'],
                date=None
            )
        )
        profile.save()
        return profile

    def create(self, validated_data):
        grade = Grade.objects.create(validated_data['grade'])
        return Profile.objects.create(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            nickname = validated_data['nickname'],
            school = validated_data['school'],
            year_of_graduation = grade.get_year_of_graduation_by_date(),
            phone = validated_data['phone'],
            parent_phone = validated_data['parent_phone'],
            gdpr = validated_data['gdpr']
        )

class ProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname']


class ProfileMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname', 'email']

    first_name = serializers.CharField(
        source='user.first_name', read_only=False)
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
