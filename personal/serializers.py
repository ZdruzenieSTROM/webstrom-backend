from django_typomatic import ts_interface
from rest_framework import serializers

from competition.models import Grade
from personal.models import County, District, Profile, School


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
    verbose_name = serializers.SerializerMethodField('get_verbose_name')
    id = serializers.SerializerMethodField('get_id')

    class Meta:
        model = School
        fields = ['id', 'code', 'name', 'abbreviation', 'street',
                  'city', 'zip_code', 'email', 'district', 'verbose_name']
        read_only_fields = ['id', 'verbose_name']

    def get_verbose_name(self, obj):
        return str(obj)

    def get_id(self, obj):
        return obj.code


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
    grade = serializers.IntegerField()
    grade_name = serializers.SerializerMethodField('get_grade_name')
    school = SchoolProfileSerializer(many=False, read_only=True)
    is_student = serializers.SerializerMethodField('get_is_student')
    has_school = serializers.SerializerMethodField('get_has_school')
    school_id = serializers.IntegerField()
    email = serializers.EmailField(source='user.email')
    verbose_name = serializers.SerializerMethodField('get_verbose_name')

    class Meta:
        model = Profile
        fields = ['grade_name', 'id', 'email', 'first_name', 'last_name', 'school',
                  'phone', 'parent_phone', 'grade', 'is_student', 'has_school',
                  'school_id', 'verbose_name']
        read_only_fields = ['grade_name', 'id', 'first_name', 'last_name',
                            'email', 'is_student', 'has_school', 'school', 'verbose_name']

        extra_kwargs = {
            'grade': {
                'validators': []
            },
            'school_id': {
                'write_only': True,
            }
        }

    def get_verbose_name(self, obj):
        return str(obj)

    def get_is_student(self, obj):
        return obj.school != School.objects.get(pk=1)

    def get_has_school(self, obj):
        return obj.school != School.objects.get(pk=0) and obj.school != School.objects.get(pk=1)

    def get_grade_name(self, obj):
        return Grade.get_grade_by_year_of_graduation(
            year_of_graduation=obj.year_of_graduation
        ).name

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
            school=validated_data['school'],
            year_of_graduation=grade.get_year_of_graduation_by_date(),
            phone=validated_data['phone'],
            parent_phone=validated_data['parent_phone']
        )


@ts_interface(context='personal')
class ProfileCreateSerializer(serializers.ModelSerializer):
    grade = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'school',
                  'phone', 'parent_phone',  'grade']
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
            school=validated_data['school'],
            year_of_graduation=grade.get_year_of_graduation_by_date(),
            phone=validated_data['phone'],
            parent_phone=validated_data['parent_phone'],
        )


@ts_interface(context='personal')
class ProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name']


@ts_interface(context='personal')
class ProfileExportSerializer(serializers.ModelSerializer):

    school_name = serializers.CharField(source='school.name')
    school_abbreviation = serializers.CharField(source='school.abbreviation')
    school_street = serializers.CharField(source='school.street')
    school_city = serializers.CharField(source='school.city')
    school_zip_code = serializers.CharField(source='school.zip_code')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Profile
        fields = ['school_name', 'school_abbreviation',
                  'school_street', 'school_city', 'school_zip_code',
                  'first_name', 'last_name', 'email']
