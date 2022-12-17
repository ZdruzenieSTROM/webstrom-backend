from django_typomatic import ts_interface
from rest_framework import serializers

from competition.models import Grade
from personal.models import County, District, Profile, School

#from competition.serializers import GradeSerializer


@ts_interface(context='personal')
class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = '__all__'


@ts_interface(context='personal')
class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


@ts_interface(context='personal')
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


@ts_interface(context='personal')
class SchoolShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        exclude = ['email', 'district']


@ts_interface(context='personal')
class SchoolProfileSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(many=False)
    verbose_name = serializers.SerializerMethodField('get_verbose_name')

    class Meta:
        model = School
        fields = ['code', 'district', 'verbose_name']

    def get_verbose_name(self, obj):
        return str(obj)


@ts_interface(context='personal')
class ProfileSerializer(serializers.ModelSerializer):
    #grade_info = GradeSerializer(many=True)
    grade = serializers.IntegerField()
    school = SchoolProfileSerializer(many=False, read_only=True)
    is_student = serializers.SerializerMethodField('get_is_student')
    has_school = serializers.SerializerMethodField('get_has_school')
    school_id = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname', 'school',
                  'phone', 'parent_phone', 'gdpr', 'grade', 'is_student', 'has_school', 'school_id']
        read_only_fields = ['first_name', 'last_name',
                            'email', 'is_student', 'has_school', 'school']  # 'year_of_graduation',
        email = serializers.EmailField(source='user.email')

        extra_kwargs = {
            'grade': {
                'validators': []
            },
            'school_id': {
                'write_only': True,
            }
        }

    def get_is_student(self, obj):
        return obj.school != School.objects.get(pk=1)

    def get_has_school(self, obj):
        return obj.school != School.objects.get(pk=0) and obj.school != School.objects.get(pk=1)

    def update(self, instance, validated_data):
        grade = Grade.objects.get(pk=validated_data.pop('grade'))
        school = School.objects.get(pk=validated_data.pop('school_id'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.school = school
        instance.year_of_graduation = grade.get_year_of_graduation_by_date()
        instance.save()
        return instance

    def create(self, validated_data):
        grade = Grade.objects.get(pk=validated_data['grade'])
        return Profile.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            nickname=validated_data['nickname'],
            school=validated_data['school'],
            year_of_graduation=grade.get_year_of_graduation_by_date(),
            phone=validated_data['phone'],
            parent_phone=validated_data['parent_phone'],
            gdpr=validated_data['gdpr']
        )


@ts_interface(context='personal')
class ProfileCreateSerializer(serializers.ModelSerializer):
    grade = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname', 'school',
                  'phone', 'parent_phone', 'gdpr', 'grade']
        read_only_fields = ['grade']
        extra_kwargs = {
            'grade': {
                'validators': []
            }
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        grade = Grade.objects.get(pk=validated_data['grade'])
        setattr(
            instance,
            'year_of_graduation',
            grade.get_year_of_graduation_by_date()
        )
        instance.save()
        return instance

    def create(self, validated_data):
        grade = Grade.objects.create(validated_data['grade'])
        return Profile.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            nickname=validated_data['nickname'],
            school=validated_data['school'],
            year_of_graduation=grade.get_year_of_graduation_by_date(),
            phone=validated_data['phone'],
            parent_phone=validated_data['parent_phone'],
            gdpr=validated_data['gdpr']
        )


@ts_interface(context='personal')
class ProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname']


@ts_interface(context='personal')
class ProfileMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'nickname', 'email']

    email = serializers.EmailField(source='user.email')
