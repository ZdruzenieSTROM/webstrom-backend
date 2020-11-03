
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

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import exceptions
from competition.serializers import ProblemSerializer, SeriesSerializer, SeriesWithProblemsSerializer, ProblemStatsSerializer, SemesterSerializer

from competition.forms import SeriesSolutionForm
from competition.models import (Competition, EventRegistration, Grade, Problem,
                                Semester, Series, Solution)
from competition.utils import generate_praticipant_invitations

from webstrom import settings


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

    @action(methods=['post'], detail=True)
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

    @action(detail=True)
    def my_solution(self, request, pk=None):
        problem = self.get_object()
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied('Je potrebné sa prihlásiť')
        event_registration = EventRegistration.get_registration_by_profile_and_event(
            request.user.profile, problem.series.semester)
        if event_registration is None:
            raise exceptions.MethodNotAllowed(method='upload-solutuion')
        pass

    @action(methods=['get'], detail=True, permission_classes=[IsAdminUser])
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
                        print(prefix)
                    _, fname = os.path.split(solution.solution.path)
                    zipf.write(solution.solution.path,
                               f'{prefix}{fname}')
        response = HttpResponse(s.getvalue(),
                                content_type="application/x-zip-compressed")

        response['Content-Disposition'] = (
            'attachment; filename=export.zip'
        )

        return response

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
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

    @action(methods=['get'], detail=True)
    def results(self, request, pk=None):
        series = self.get_object()
        return Response(series.results())

    @action(methods=['get'], detail=True)
    def stats(self, request, pk=None):
        problems = self.get_object().problems

        return


class SolutionViewSet(viewsets.ModelViewSet):
    pass


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    #permission_classes = (UserPermission,)


class SeriesProblemsView(DetailView):
    template_name = 'competition/series.html'
    model = Series

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO: táto logika sa opakuje na viacerých miestach
        if hasattr(self.request.user, 'profile'):
            context['profile'] = self.request.user.profile
            context['registration'] = EventRegistration.get_registration_by_profile_and_event(
                self.request.user.profile, self.object.semester)
        else:
            context['profile'] = context['registration'] = None

        context['form'] = form = SeriesSolutionForm(self.object)
        context['problems'] = zip(self.object.problems.all(), form)
        return context

    def post(self, request, **kwargs):
        # pylint: disable=unused-argument, attribute-defined-outside-init
        self.object = self.get_object()

        form = SeriesSolutionForm(
            self.object,
            data=request.POST,
            files=request.FILES)

        try:
            registration = EventRegistration.get_registration_by_profile_and_event(
                self.request.user.profile, self.object.semester)
            assert form.is_valid()
        except AttributeError:
            messages.error(
                request, 'Na odovzdávanie riešení je potrebné sa prihlásiť')
        except (EventRegistration.DoesNotExist, AssertionError):
            messages.error(request, 'Odovzdávanie riešení zlyhalo')
        else:
            for field in form.fields:
                if field not in request.FILES:
                    continue

                problem = Problem.objects.get(pk=int(field))

                solution, _ = Solution.objects.get_or_create(
                    semester_registration=registration,
                    problem=problem
                )

                solution.solution = request.FILES[field]
                solution.is_online = True
                solution.save()

                messages.success(
                    request, f'{problem.pk}: Riešenie bolo úspešne odovzdané')

        return self.get(request)


class LatestSeriesProblemsView(SeriesProblemsView):
    def get_object(self, queryset=None):
        # TODO: treba dorobit metodu co vrati aktualnu seriu a to tu capnut
        return Competition.get_seminar_by_current_site().semester_set\
            .order_by('-end').first().series_set.first()


class ArchiveView(ListView):
    # TODO: toto prerobím keď pribudne model ročník
    template_name = 'competition/archive.html'
    model = Semester
    context_object_name = 'context'

    def get_queryset(self):
        site_competition = Competition.get_seminar_by_current_site()
        context = {}
        years = {}

        for sem in Semester.objects.filter(competition=site_competition).order_by('-year'):
            if not sem.year in years:
                years[sem.year] = []
            years[sem.year].append(sem)

        context["mostRecentYear"] = Semester.objects.filter(
            competition=site_competition).order_by('-year').first().year
        context["years"] = years
        return context


class SeriesResultsView(DetailView):
    model = Series
    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "profile" in dir(self.request.user):
            context['profile'] = self.request.user.profile
            context['registration'] = EventRegistration.get_registration_by_profile_and_event(
                self.request.user.profile, self.object.semester)
        else:
            context['profile'] = context['registration'] = None

        context['results'] = self.object.results_with_ranking()
        context['results_type'] = 'series'
        return context


class SemesterResultsView(DetailView):
    model = Semester
    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "profile" in dir(self.request.user):
            context['profile'] = self.request.user.profile
            context['registration'] = EventRegistration.get_registration_by_profile_and_event(
                self.request.user.profile, self.object)
        else:
            context['profile'] = context['registration'] = None

        context['results'] = self.object.results_with_ranking()
        context['results_type'] = 'semester'

        return context


class SeriesResultsLatexView(SeriesResultsView):
    template_name = 'competition/results_latex.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['histograms'] = []
        for problem in self.object.problems.all():
            context['histograms'].append(problem.get_stats())
        context['schools'] = self.object.semester.get_schools()
        context['schools_offline'] = self.object.semester.get_schools(
            offline_users_only=True)
        return context


class SemesterResultsLatexView(SemesterResultsView):
    template_name = 'competition/results_latex.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schools'] = self.object.get_schools()
        context['schools_offline'] = self.object.get_schools(
            offline_users_only=True)
        return context


class SemesterInvitationsLatexView(DetailView):
    model = Semester
    template_name = 'competition/invitations_latex/invitations_latex.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        participants = generate_praticipant_invitations(
            self.object.results_with_ranking(),
            self.kwargs.get('num_participants', 32),
            self.kwargs.get('num_substitutes', 20),
        )
        participants.sort(key=itemgetter('first_name'))
        participants.sort(key=itemgetter('last_name'))
        context['participants'] = participants

        schools = {}
        for participant in participants:
            if participant['school'] in schools:
                schools[participant['school']].append(participant)
            else:
                schools[participant['school']] = [participant]
        context['schools'] = schools

        return context


class SemesterRegistrationView(View):
    def get(self, request, pk, cont, **kwargs):
        # pylint: disable=unused-argument, invalid-name
        try:
            profile = self.request.user.profile
            semester = Semester.objects.get(pk=pk)
            assert not EventRegistration.get_registration_by_profile_and_event(
                profile, semester)
            EventRegistration(
                profile=profile, school=profile.school,
                grade=Grade.get_grade_by_year_of_graduation(
                    profile.year_of_graduation),
                event=semester).save()
        except AssertionError:
            messages.info(
                request, 'Do semestra sa dá registrovať iba jedenkrát')
        except AttributeError:
            messages.error(request, 'Na registráciu je potrebné sa prihlásiť')
        else:
            messages.success(
                request,
                f'{Semester.objects.get(pk=pk)}: Registrácia do semestra prebehla úspešne')

        return redirect(cont)


class SemesterPublicationView(DetailView):
    model = Semester
    template_name = 'competition/publication.html'
