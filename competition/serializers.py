import datetime

from django.contrib.auth.models import AnonymousUser
from django.core import exceptions
from django_typomatic import ts_interface
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from base.validators import school_year_validator
from competition import models
from personal.serializers import ProfileShortSerializer, SchoolShortSerializer


class ModelWithParticipationSerializer(serializers.ModelSerializer):
    can_participate = serializers.SerializerMethodField('get_can_participate')
    is_registered = serializers.SerializerMethodField('get_is_registered')

    def get_can_participate(self, obj):
        if 'request' in self.context and hasattr(self.context['request'].user, 'profile'):
            return obj.can_user_participate(self.context['request'].user)
        return None

    def get_event(self, obj):
        return obj

    def get_is_registered(self, obj):
        if 'request' in self.context and hasattr(self.context['request'].user, 'profile'):
            return models.EventRegistration.get_registration_by_profile_and_event(
                self.context['request'].user.profile, self.get_event(obj)
            ) is not None
        return None


@ts_interface(context='competition')
class PublicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublicationType
        fields = '__all__'


@ts_interface(context='competition')
class PublicationSerializer(serializers.ModelSerializer):
    verbose_name = serializers.SerializerMethodField('get_verbose_name')

    class Meta:
        model = models.Publication
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['file'].parent = None

    def get_verbose_name(self, obj):
        return str(obj)


@ts_interface(context='competition')
class RegistrationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegistrationLink
        fields = '__all__'


@ts_interface(context='competition')
class EventSerializer(ModelWithParticipationSerializer):
    verbose_name = serializers.SerializerMethodField('get_verbose_name')
    publication_set = PublicationSerializer(many=True, read_only=True)
    registration_link = RegistrationLinkSerializer(
        many=False,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = models.Event
        fields = '__all__'

    def validate_school_year(self, value: str):
        try:
            school_year_validator(value)
            return value
        except exceptions.ValidationError as exc:
            raise ValidationError('Nesprávny formát šk. roku') from exc

    def validate(self, attrs):
        school_year = attrs.get('school_year')
        start_year, end_year = school_year.split('/')
        start = attrs.get('start')
        end = attrs.get('end')
        if start and start.date() < datetime.date(year=int(start_year), month=7, day=1):
            raise ValidationError(
                f'Začiatok súťaže ({start}) nie je v školskom roku {school_year}')
        if end and end.date() > datetime.date(year=int(end_year), month=8, day=31):
            raise ValidationError(
                f'Koniec súťaže ({end}) nie je v školskom roku {school_year}')
        return super().validate(attrs)

    def create(self, validated_data):
        registration_link = validated_data.pop('registration_link', None)

        if registration_link is not None:
            registration_link = models.RegistrationLink.objects.create(
                **registration_link,
            )

        return models.Event.objects.create(
            registration_link=registration_link,
            **validated_data,
        )

    def get_verbose_name(self, obj):
        return str(obj)


@ts_interface(context='competition')
class CompetitionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompetitionType
        fields = '__all__'


@ts_interface(context='competition')
class CompetitionSerializer(serializers.ModelSerializer):
    competition_type = CompetitionTypeSerializer(many=False, read_only=True)
    upcoming_or_current_event = serializers.SerializerMethodField(
        'get_upcoming_or_current_event')
    history_events = serializers.SerializerMethodField('get_history_events')

    class Meta:
        model = models.Competition
        exclude = ['permission_group']
        read_only_fields = [
            'upcoming_or_current_event',
            'history_events',
            'competition_type',
            'name',
            'slug',
            'start_year',
            'min_years_until_graduation',
            'sites'
        ]

    def get_upcoming_or_current_event(self, obj):
        try:
            return EventSerializer(obj.event_set.upcoming_or_current()).data
        except models.Event.DoesNotExist:
            return None

    def get_history_events(self, obj):
        return EventSerializer(obj.event_set.history(), many=True).data


@ts_interface(context='competition')
class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grade
        exclude = ['is_active']


@ts_interface(context='competition')
class EventRegistrationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventRegistration
        fields = ['school', 'grade', 'profile', 'verbose_name', 'id', 'event']
    school = SchoolShortSerializer(many=False)
    grade = GradeSerializer(many=False)
    profile = ProfileShortSerializer(many=False)
    verbose_name = serializers.SerializerMethodField('get_verbose_name')

    def get_verbose_name(self, obj):
        return str(obj)


class EventRegistrationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventRegistration
        fields = ['school', 'grade', 'profile', 'id', 'event']

    id = serializers.ReadOnlyField()
    school = serializers.PrimaryKeyRelatedField(
        queryset=models.School.objects.all())
    grade = serializers.PrimaryKeyRelatedField(
        queryset=models.Grade.objects.all())
    profile = serializers.PrimaryKeyRelatedField(
        queryset=models.Profile.objects.all())
    event = serializers.PrimaryKeyRelatedField(
        queryset=models.Event.objects.all())

    def validate(self, attrs):
        grade: models.Grade | None = attrs.get('grade')
        event: models.Event | None = attrs.get('event')
        if event and grade and (
            event.competition.min_years_until_graduation > grade.years_until_graduation
        ):
            raise ValidationError(
                f'Ročník {grade.tag} nie je povolený pre {event.competition.name}')
        return super().validate(attrs)


@ts_interface(context='competition')
class ProblemCorrectionSerializer(serializers.ModelSerializer):
    corrected_by = serializers.SerializerMethodField('get_corrected_by')
    best_solution = serializers.SerializerMethodField('get_best_solution')

    class Meta:
        model = models.ProblemCorrection
        fields = ['corrected_by', 'best_solution']

    def get_corrected_by(self, obj):
        return [user.profile.get_full_name() for user in obj.corrected_by.all()]

    def get_best_solution(self, obj):
        return [
            solution.semester_registration.profile.get_full_name()
            for solution in obj.best_solution.all()
        ]


@ts_interface(context='competition')
class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Problem
        fields = '__all__'
        read_only_fields = ['submitted', 'num_comments',
                            'num_solutions', 'num_corrected_solutions']

    submitted = serializers.SerializerMethodField(
        'get_submitted')
    num_comments = serializers.SerializerMethodField(
        'get_num_comments')
    num_solutions = serializers.SerializerMethodField('get_num_solutions')
    num_corrected_solutions = serializers.SerializerMethodField(
        'get_num_corrected_solutions')
    verbose_name = serializers.SerializerMethodField('get_verbose_name')
    # correction = ProblemCorrectionSerializer(many=False,)

    def get_num_comments(self, obj):
        """Get number of comments related to problem"""
        user = self.context['request'].user if 'request' in self.context else AnonymousUser
        return len(list(obj.get_comments(user)))

    def get_num_solutions(self, obj: models.Problem):
        return obj.num_solutions

    def get_num_corrected_solutions(self, obj: models.Problem):
        return obj.num_corrected_solutions

    def get_submitted(self, obj):
        if 'request' in self.context:
            if (
                self.context['request'].user.is_anonymous or
                not hasattr(self.context['request'].user, 'profile')
            ):
                return None

            semester_registration = models.EventRegistration.get_registration_by_profile_and_event(
                self.context['request'].user.profile, obj.series.semester)

            try:
                solution = obj.solution_set.filter(
                    semester_registration=semester_registration).latest('uploaded_at')
            except models.Solution.DoesNotExist:
                return None
            return SolutionSerializer(solution).data
        return None

    def get_verbose_name(self, obj):
        return str(obj)


@ts_interface(context='competition')
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'

    posted_by_name = serializers.SerializerMethodField('get_posted_by_name')
    edit_allowed = serializers.SerializerMethodField('get_edit_allowed')

    def get_posted_by_name(self, obj: models.Comment):
        return obj.posted_by.profile.get_full_name()

    def get_edit_allowed(self, obj: models.Comment):
        if 'request' in self.context:
            return obj.can_user_modify(self.context['request'].user)
        return None


@ts_interface(context='competition')
class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Solution
        fields = '__all__'


@ts_interface(context='competition')
class SolutionAdministrationSerializer(serializers.ModelSerializer):
    semester_registration = EventRegistrationReadSerializer(read_only=True)

    class Meta:
        model = models.Solution
        fields = ['id', 'corrected_solution', 'vote', 'solution',
                  'late_tag', 'score', 'semester_registration', 'is_online']
        read_only_fields = ['corrected_solution',
                            'semester_registration']


@ts_interface(context='competition')
class SeriesSerializer(serializers.ModelSerializer):
    complete = serializers.SerializerMethodField('get_complete')

    class Meta:
        model = models.Series
        read_only_fields = ['complete']
        fields = ['id', 'semester', 'order', 'deadline', 'complete']

    def get_complete(self, obj: models.Series):
        return obj.complete


@ts_interface(context='competition')
class ProblemWithSolutionsSerializer(serializers.ModelSerializer):
    solution_set = SolutionAdministrationSerializer(many=True)
    correction = ProblemCorrectionSerializer(many=False)
    series = SeriesSerializer()

    histogram = serializers.SerializerMethodField('get_histogram')
    total_solutions = serializers.SerializerMethodField(
        'get_total_solutions')
    tex_header = serializers.SerializerMethodField('get_tex_header')

    class Meta:
        model = models.Problem
        fields = ['histogram', 'total_solutions', 'solution_set', 'text', 'order',
                  'correction', 'series', 'solution_pdf',
                  'tex_header']
        read_only_fields = ['histogram', 'tex_header'
                            'num_solutions', 'text', 'order', 'series']

    def format_list_of_names(self, names: list[str]) -> str:
        if names is None or len(names) == 0:
            return ''
        if len(names) == 1:
            return names[0]
        return ', '.join(names[:-1])+' a '+names[-1]

    def format_histogram(self, histogram: list[dict[str, int]]) -> str:
        return ''.join([f'({item["score"]},{item["count"]})' for item in histogram])

    def get_tex_header(self, obj: models.Problem) -> str:
        """Generuje tex hlavicku vzoraku do casaku"""
        try:
            corrected_by = [user.profile.get_full_name()
                            for user in obj.correction.corrected_by.all()]
            corrected_suffix = 'i' if len(corrected_by) > 1 else ''

            best_solutions = [user.profile.get_full_name()
                              for user in obj.correction.corrected_by.all()]
            best_solution_suffix = 'e' if len(best_solutions) > 1 else 'a'
        except models.Problem.correction.RelatedObjectDoesNotExist:  # pylint: disable=no-member
            corrected_by = None
            corrected_suffix = ''
            best_solutions = None
            best_solution_suffix = 'a'
        num_solutions = self.get_total_solutions(obj)
        histogram = self.get_histogram(obj)
        return f'\\vzorak{{{corrected_suffix}}}'\
            f'{{{self.format_list_of_names(corrected_by)}}}'\
            f'{{{num_solutions}}}'\
            f'{{{best_solution_suffix}}}'\
            f'{{{self.format_list_of_names(best_solutions)}}}'\
            f'{{{self.format_histogram(histogram)}}}'

    def get_histogram(self, obj):
        return models.Problem.get_stats(obj).get('histogram')

    def get_total_solutions(self, obj):
        return models.Problem.get_stats(obj).get('num_solutions')


@ts_interface(context='competition')
class SeriesWithProblemsSerializer(ModelWithParticipationSerializer):
    problems = ProblemSerializer(
        many=True,
        read_only=True
    )
    can_submit = serializers.SerializerMethodField('get_can_submit')
    can_resubmit = serializers.SerializerMethodField('get_can_resubmit')
    complete = serializers.SerializerMethodField('get_complete')
    verbose_name = serializers.SerializerMethodField('get_verbose_name')

    class Meta:
        model = models.Series
        exclude = ['sum_method', 'frozen_results']
        include = ['complete', 'problems', 'can_submit',
                   'can_resubmit', 'verbose_name']
        read_only_fields = [
            'complete',
            'can_submit', 'can_resubmit', 'verbose_name']

    def get_can_submit(self, obj):
        return obj.can_submit

    def get_complete(self, obj: models.Series):
        return obj.complete

    def get_can_resubmit(self, obj):
        return obj.can_resubmit

    def get_event(self, obj):
        return obj.semester

    def get_verbose_name(self, obj):
        return str(obj)


@ts_interface(context='competition')
class SemesterSerializer(serializers.ModelSerializer):
    series_set = SeriesSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = models.Semester
        fields = '__all__'
        read_only_fields = ['series_set', 'publication_set']
        extra_kwargs = {
            'frozen_results': {'write_only': True}
        }


@ts_interface(context='competition')
class SemesterWithProblemsSerializer(ModelWithParticipationSerializer):
    series_set = SeriesWithProblemsSerializer(
        many=True,
        read_only=True
    )
    publication_set = PublicationSerializer(many=True, read_only=True)
    complete = serializers.SerializerMethodField('get_complete')
    verbose_name = serializers.SerializerMethodField('get_verbose_name')

    class Meta:
        model = models.Semester
        exclude = ['frozen_results', 'registration_link']
        read_only_fields = ['complete']
        validators = []

    def validate_season_code(self, value: int):
        if value not in (0, 1):
            raise ValidationError(
                'Seminár musí byť zimný alebo letný(season_code 0 alebo 1)')
        return value

    def validate_competition(self, value: models.Competition):
        if value and value.competition_type.name != "Seminár":
            raise ValidationError('Súťaž nie je typu seminár')
        return value

    def validate_school_year(self, value: str):
        try:
            school_year_validator(value)
            return value
        except exceptions.ValidationError as exc:
            raise ValidationError('Nesprávny formát šk. roku') from exc

    def validate(self, attrs):
        school_year = attrs.get('school_year')
        if school_year is not None:
            start = attrs.get('start')
            end = attrs.get('end')
            start_year, end_year = school_year.split('/')
            if start and start.date() < datetime.date(year=int(start_year), month=7, day=1):
                raise ValidationError(
                    f'Začiatok súťaže ({start}) nie je v školskom roku {school_year}')
            if end and end.date() > datetime.date(year=int(end_year), month=8, day=31):
                raise ValidationError(
                    f'Koniec súťaže ({end}) nie je v školskom roku {school_year}')
        return super().validate(attrs)

    def get_complete(self, obj: models.Semester):
        return obj.complete

    def update(self, instance: models.Semester, validated_data):
        late_tags = validated_data.pop('late_tags', [])
        instance.late_tags.clear()
        for tag in late_tags:
            instance.late_tags.add(tag)
        return super().update(instance, validated_data)

    def create(self, validated_data: dict):
        late_tags = validated_data.pop('late_tags', [])
        semester = models.Semester.objects.create(**validated_data)
        for tag in late_tags:
            semester.late_tags.add(tag)
        return semester

    def get_verbose_name(self, obj):
        return str(obj)


@ts_interface(context='competition')
class LateTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LateTag
        exclude = ['comment']
