
from io import BytesIO
import json
from operator import itemgetter
import os
import zipfile

from base.utils import mime_type

from django.contrib import messages
from django.core.files.move import file_move_safe
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, View

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import exceptions
from competition.serializers import EventSerializer, EventRegistrationSerializer, ProblemSerializer, SeriesSerializer, SeriesWithProblemsSerializer, SemesterSerializer, SemesterWithProblemsSerializer, SolutionSerializer
from profile.serializers import SchoolSerializer

from competition.models import (Competition, Event, EventRegistration, Grade, Problem,
                                Semester, Series, Solution, Vote)
from competition import utils
from profile.models import School

from user.models import User

from webstrom import settings

# pylint: disable=unused-argument


class ProblemViewSet(viewsets.ModelViewSet):
    """
    Obsluhuje API endpoint pre Úlohy
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    # permission_classes = (UserPermission,)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminUser])
    def stats(self, request, pk=None):
        return Response(self.get_object().get_stats())

    @action(methods=['post'], detail=True, url_name='upload-solution')
    def upload_solution(self, request, pk=None):
        problem = self.get_object()
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied('Je potrebné sa prihlásiť')
        event_registration = EventRegistration.get_registration_by_profile_and_event(
            request.user.profile, problem.series.semester)
        if event_registration is None:
            raise exceptions.MethodNotAllowed(method='upload-solutuion')
        elif 'file' not in request.data:
            raise exceptions.ParseError(detail='Request neobsahoval súbor')
        else:
            f = request.data['file']
            if mime_type(f) != 'application/pdf':
                raise exceptions.ParseError(
                    detail='Riešenie nie je vo formáte pdf')
            late_tag = problem.series.get_actual_late_flag()
            solution = Solution.objects.create(
                problem=problem,
                semester_registration=event_registration,
                late_tag=late_tag,
                is_online=True
            )
            solution.solution.save(
                solution.get_solution_file_name(), f, save=True)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, url_path='my-solution')
    def my_solution(self, request, pk=None):
        problem = self.get_object()
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied('Je potrebné sa prihlásiť')
        event_registration = EventRegistration.get_registration_by_profile_and_event(
            request.user.profile, problem.series.semester)
        if event_registration is None:
            raise exceptions.MethodNotAllowed(method='my-solution')
        solution = Solution.objects.filter(
            problem=problem, semester_registration=event_registration).first()
        serializer = SolutionSerializer(solution)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminUser], url_path='download-solutions')
    def download_solutions(self, request, pk=None):
        solutions = self.get_object().solution_set.all()
        # Open StringIO to grab in-memory ZIP contents
        s = BytesIO()
        with zipfile.ZipFile(s, 'w') as zipf:
            for solution in solutions:
                if solution.is_online and solution.solution.name is not None:
                    prefix = ''
                    if solution.late_tag is not None:
                        prefix = f'{solution.late_tag.slug}/'
                    _, fname = os.path.split(solution.solution.path)
                    zipf.write(solution.solution.path,
                               f'{prefix}{fname}')
        response = HttpResponse(s.getvalue(),
                                content_type="application/x-zip-compressed")

        response['Content-Disposition'] = (
            'attachment; filename=export.zip'
        )

        return response

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser], url_path='upload-corrected')
    def upload_solutions_with_points(self, request, pk=None):
        if 'file' not in request.data:
            raise exceptions.ParseError(detail='No file attached')
        zfile = request.data['file']
        if not zipfile.is_zipfile(zfile):
            raise exceptions.ParseError(
                detail='Attached file is not a zip file')
        zfile = zipfile.ZipFile(zfile)
        if zfile.testzip():
            raise exceptions.ParseError(detail='Zip file is corrupted')
        pdf_files = [name for name in zfile.namelist()
                     if name.endswith('.pdf')]
        status = []
        for filename in pdf_files:
            try:
                parts = filename.rstrip('.pdf').split('-')
                score = int(parts[0])
                problem_pk = int(parts[-2])
                registration_pk = int(parts[-1])
                event_reg = EventRegistration.objects.get(pk=registration_pk)
                solution = Solution.objects.get(semester_registration=event_reg,
                                                problem=problem_pk)
            except (IndexError, ValueError, AssertionError):
                status.append({
                    'filename': filename,
                    'status': 'Cannot parse file'
                })
                continue
            except EventRegistration.DoesNotExist:
                status.append({
                    'filename': filename,
                    'status': f'User registration with id {registration_pk} does not exist'
                })
                continue
            except Solution.DoesNotExist:
                status.append({
                    'filename': filename,
                    'status': f'Solution with registration id {registration_pk} and problem id {problem_pk} does not exist'
                })
                continue

            extracted_path = zfile.extract(filename, path='/tmp')
            new_path = os.path.join(
                settings.MEDIA_ROOT, 'solutions', solution.get_corrected_solution_file_name())
            file_move_safe(extracted_path, new_path, allow_overwrite=True)

            solution.score = score
            solution.corrected_solution = solution.get_corrected_solution_file_name()
            solution.save()
            status.append({
                'filename': filename,
                'status': f'OK - points: {score}'
            })
        return Response(json.dumps(status))


class SeriesViewSet(viewsets.ModelViewSet):
    """
    Obsluhuje API endpoint pre Úlohy
    """
    queryset = Series.objects.all()
    serializer_class = SeriesWithProblemsSerializer
    # permission_classes = (UserPermission,)

    @staticmethod
    def _create_profile_dict(series, sum_func, semester_registration, profile_solutions):
        # list primary keys uloh v aktualnom semestri
        problems_pk_list = []
        for problem in series.problems.all():
            problems_pk_list.append(problem.pk)
        solutions = []
        for points, sol, problem in zip(utils.solutions_to_list_of_points_pretty(profile_solutions), profile_solutions, problems_pk_list):
            solutions.append({
                'points': points,
                'solution_pk': sol.pk if sol else None,
                'problem_pk': problem
            })
        profile = EventRegistrationSerializer(semester_registration)
        return {
            # Poradie - horná hranica, v prípade deleného miesto(napr. 1.-3.) ide o nižšie miesto(1)
            'rank_start': 0,
            # Poradie - dolná hranica, v prípade deleného miesto(napr. 1.-3.) ide o vyššie miesto(3)
            'rank_end': 0,
            # Indikuje či sa zmenilo poradie od minulej priečky, slúži na delené miesta
            'rank_changed': True,
            # primary key riešiteľovej registrácie do semestra
            'registration': profile.data,
            # Súčty bodov po sériách
            'subtotal': [sum_func(profile_solutions, semester_registration)],
            # Celkový súčet za danú entitu
            'total': sum_func(profile_solutions, semester_registration),
            # zipnutý zoznam riešení a pk príslušných problémov,
            # aby ich bolo možné prelinkovať z poradia do admina
            # a získať pk problému pri none riešení
            'solutions': [solutions]
        }

    @ staticmethod
    def series_results(series):
        sum_func = getattr(utils, series.sum_method or '',
                           utils.series_simple_sum)
        results = []

        solutions = Solution.objects.only('semester_registration', 'problem', 'score')\
            .filter(problem__series=series)\
            .order_by('semester_registration', 'problem')\
            .select_related('semester_registration', 'problem')

        current_profile = None
        profile_solutions = [None] * series.num_problems

        for solution in solutions:
            if current_profile != solution.semester_registration:
                if current_profile:
                    # Bolo dokončené spracovanie jedného usera
                    # Zbali usera a a nahodi ho do vysledkov
                    results.append(SeriesViewSet._create_profile_dict(series,
                                                                      sum_func, current_profile, profile_solutions))
                # vytvori prazdny list s riešeniami
                current_profile = solution.semester_registration
                profile_solutions = [None] * series.num_problems

            # Spracuj riešenie
            profile_solutions[solution.problem.order - 1] = solution

        # Uloz posledneho usera
        if current_profile:
            results.append(SeriesViewSet._create_profile_dict(series,
                                                              sum_func, current_profile, profile_solutions))

        return results

    @ action(methods=['get'], detail=True)
    def results(self, request, pk=None):
        series = self.get_object()
        if series.frozen_results is not None:
            return series.frozen_results
        results = self.series_results(series)
        results.sort(key=itemgetter('total'), reverse=True)
        results = utils.rank_results(results)
        return Response(results, status=status.HTTP_201_CREATED)

    @ action(methods=['get'], detail=True)
    def stats(self, request, pk=None):
        problems = self.get_object().problems
        stats = []
        for problem in problems:
            stats.append(problem.get_stats())
        return Response(stats, status=status.HTTP_200_OK)

    @ action(methods=['get'], detail=False)
    def current(self, request):
        items = Series.objects.all()\
            .filter(complete=False)\
            .order_by('-deadline')\
            .first()
        serializer = SeriesWithProblemsSerializer(items, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SolutionViewSet(viewsets.ModelViewSet):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer

    def add_vote(self, request, positive, solution):
        if solution.votes.count() > 0:
            return Response(status=status.HTTP_409_CONFLICT)
        if 'comment' in request.data:
            Vote.objects.create(
                solution=solution, is_positive=positive, comment=request.data['comment'])
        else:
            Vote.objects.create(solution=solution, is_positive=positive)
        return Response(status=status.HTTP_201_CREATED)

    @ action(methods=['post'], detail=True, url_path='add-positive-vote', permission_classes=[IsAdminUser])
    def add_positive_vote(self, request, pk=None):
        solution = self.get_object()
        return self.add_vote(request, True, solution)

    @ action(methods=['post'], detail=True, url_path='add-negative-vote', permission_classes=[IsAdminUser])
    def add_negative_vote(self, request, pk=None):
        solution = self.get_object()
        return self.add_vote(request, False, solution)

    @ action(methods=['post'], detail=True, url_path='remove-vote', permission_classes=[IsAdminUser])
    def remove_vote(self, request, pk=None):
        solution = self.get_object()
        Vote.objects.filter(solution=solution).delete()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='download-solution')
    def download_solution(self, request, pk=None):
        solution = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{solution.solution}"'
        return response

    @action(methods=['get'], detail=True, url_path='download-corrected')
    def download_corrected(self, request, pk=None):
        solution = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{solution.corrected_solution}"'
        return response


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterWithProblemsSerializer
    # permission_classes = (UserPermission,)

    @staticmethod
    def semester_results(semester):
        if semester.frozen_results is not None:
            return semester.frozen_results
        current_results = None
        curent_number_of_problems = 0
        for series in semester.series_set.all():
            series_result = SeriesViewSet.series_results(series)
            count = series.num_problems
            current_results = utils.merge_results(
                current_results, series_result, curent_number_of_problems, count)
            curent_number_of_problems += count
        current_results.sort(key=itemgetter('total'), reverse=True)
        current_results = utils.rank_results(current_results)
        return current_results

    @ action(methods=['get'], detail=True)
    def results(self, request, pk=None):
        semester = self.get_object()
        current_results = SemesterViewSet.semester_results(semester)
        return Response(current_results, status=status.HTTP_201_CREATED)

    @ action(methods=['get'], detail=True)
    def schools(self, request, pk=None):
        schools = School.objects.filter(eventregistration__event=pk)\
            .distinct()\
            .order_by('city', 'street')
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

    @ action(methods=['get'], detail=True, url_path='offline-schools')
    def offline_schools(self, request, pk=None):
        schools = School.objects.filter(eventregistration__event=pk)\
            .filter(eventregistration__solution__is_online=False)\
            .distinct()\
            .order_by('city', 'street')
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

    @ action(methods=['get'], detail=True, url_path=r'invitations/(?P<num_participants>\d+)/(?P<num_substitutes>\d+)')
    def invitations(self, request, pk=None, num_participants=32, num_substitutes=20):
        semester = self.get_object()
        num_participants = int(num_participants)
        num_substitutes = int(num_substitutes)
        participants = utils.generate_praticipant_invitations(
            SemesterViewSet.semester_results(semester),
            num_participants,
            num_substitutes
        )
        participants.sort(key=itemgetter('first_name'))
        participants.sort(key=itemgetter('last_name'))

        return Response(participants, status=status.HTTP_200_OK)

    @ action(methods=['get'], detail=True, url_path=r'school-invitations/(?P<num_participants>\d+)/(?P<num_substitutes>\d+)')
    def school_invitations(self, request, pk=None, num_participants=32, num_substitutes=20):
        num_participants = int(num_participants)
        num_substitutes = int(num_substitutes)
        semester = self.get_object()
        participants = utils.generate_praticipant_invitations(
            SemesterViewSet.semester_results(semester),
            num_participants,
            num_substitutes
        )
        participants.sort(key=itemgetter('first_name'))
        participants.sort(key=itemgetter('last_name'))
        participants.sort(key=lambda p: p['school']['code'])
        last_school = None
        schools = []
        for participant in participants:
            if last_school != participant['school']:
                last_school = participant['school']
                schools.append(
                    {'school_name': last_school, 'participants': []})
            schools[-1]['participants'].append(participant)

        return Response(schools, status=status.HTTP_200_OK)

    @ action(methods=['get'], detail=False)
    def current(self, request):
        from datetime import datetime
        items = Semester.objects.all()\
            .filter(start__lt=datetime.now())\
            .filter(end__gt=datetime.now())\
            .order_by('-end')
        if items.count() > 0:
            serializer = SemesterWithProblemsSerializer(items[0], many=False)
            return Response(serializer.data)
        else:
            serializer = SemesterWithProblemsSerializer(items, many=True)
            return Response(serializer.data)

    @ action(methods=['get'], detail=False, url_path='current-results')
    def current_results(self, request):
        from datetime import datetime
        items = Semester.objects.all()\
            .filter(start__lt=datetime.now())\
            .filter(end__gt=datetime.now())\
            .order_by('-end')
        if items.count() > 0:
            semester = items[0]
            current_results = SemesterViewSet.semester_results(semester)
            return Response(current_results, status=status.HTTP_201_CREATED)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ['school_year', 'competition', ]

    @ action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        profile = request.user.profile
        # TODO: Overiť či sa môže registrovať ... či nie je starý
        if EventRegistration.get_registration_by_profile_and_event(
                profile, event):
            return Response(status=status.HTTP_409_CONFLICT)
        EventRegistration.objects.create(
            event=event,
            school=profile.school,
            profile=profile,
            grade=Grade.get_grade_by_year_of_graduation(
                profile.year_of_graduation),

        )
        return Response(status=status.HTTP_201_CREATED)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    filterset_fields = ['event', 'profile', ]
