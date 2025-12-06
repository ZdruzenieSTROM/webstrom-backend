# pylint:disable=too-many-lines

import csv
import json
import zipfile
from io import BytesIO
from operator import itemgetter
from typing import Optional

from django.core.exceptions import ValidationError as CoreValidationError
from django.core.files import File
from django.core.mail import send_mail, send_mass_mail
# pylint: disable=unused-argument
from django.db.models.manager import BaseManager
from django.http import FileResponse, Http404, HttpResponse
from django.template.loader import render_to_string
from django_filters import Filter, FilterSet, ModelChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from base.utils import mime_type
from competition.filters import UpcomingFilter
from competition.models import (SERIES_SUM_METHODS, Comment, Competition,
                                CompetitionType, Event, EventRegistration,
                                Grade, LateTag, Problem, Publication,
                                PublicationType, Semester, Series, Solution,
                                Vote)
from competition.permissions import (CommentPermission,
                                     CompetitionRestrictedPermission,
                                     ProblemPermission)
from competition.results import (FreezingNotClosedResults,
                                 UserHasInvalidSchool, freeze_semester_results,
                                 freeze_series_results,
                                 generate_praticipant_invitations,
                                 semester_results, series_results)
from competition.serializers import (CommentSerializer, CompetitionSerializer,
                                     CompetitionTypeSerializer,
                                     EventRegistrationReadSerializer,
                                     EventRegistrationWriteSerializer,
                                     EventSerializer, GradeSerializer,
                                     LateTagSerializer, ProblemSerializer,
                                     ProblemWithSolutionsSerializer,
                                     PublicationSerializer,
                                     PublicationTypeSerializer,
                                     SemesterSerializer,
                                     SemesterWithProblemsSerializer,
                                     SeriesWithProblemsSerializer,
                                     SolutionSerializer)
from competition.utils.validations import validate_points
from personal.models import Profile, School
from personal.serializers import ProfileExportSerializer, SchoolSerializer


class ModelViewSetWithSerializerContext(viewsets.ModelViewSet):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class CompetitionViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """Naše aktivity"""
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = (CompetitionRestrictedPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['slug', 'sites', 'competition_type']
    search_fields = ['name']
    ordering_fields = ['name', 'start_year', 'competition_type']
    ordering = ['start_year']

    @action(detail=False, url_path=r'slug/(?P<slug>\w+)')
    def slug(self, request: Request, slug: str = None) -> Response:
        try:
            competition: Competition = self.get_queryset().get(slug=slug)

            return Response(
                CompetitionSerializer(competition, many=False).data
            )

        except Competition.DoesNotExist as exc:
            raise Http404 from exc


class CompetitionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CompetitionType.objects.all()
    serializer_class = CompetitionTypeSerializer


class CommentViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Komentáre(otázky) k úlohám"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CommentPermission, )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(methods=['post'], detail=True)
    def publish(self, request, pk=None):
        """Publikovanie, teda zverejnenie komentára"""
        comment: Comment = self.get_object()
        comment.publish()

        emails_to_send = [
            ('Zverejnený komentár',
             render_to_string(
                 'competition/emails/comment_published.txt',
                 context={
                     'comment': comment.text,
                     'problem': comment.problem
                 }),
             None,
             [comment.posted_by.email])
        ]

        user_notification_email_text = render_to_string(
            'competition/emails/comment_added_to_problem.txt',
            context={
                'problem': comment.problem,
                'from_stuff': comment.from_staff,
                'comment': comment.text
            })
        emails_to_send += [
            ('Nový komentár', user_notification_email_text, None, [user.email])
            for user in comment.problem.get_users_in_comment_thread() if user != comment.posted_by]
        send_mass_mail(emails_to_send)

        comment.save()

        return Response("Komentár bol publikovaný.", status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def hide(self, request, pk=None):
        """Skrytie komentára"""
        comment: Comment = self.get_object()
        comment.hide(message=request.data.get('hidden_response'))

        send_mail(
            'Skrytý komentár',
            render_to_string('competition/emails/comment_hidden.txt',
                             context={
                                 'comment': comment.text,
                                 'problem': comment.problem,
                                 'response': comment.hidden_response
                             }),
            None,
            [comment.posted_by.email],
        )

        comment.save()

        return Response("Komentár bol skrytý.", status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def edit(self, request, pk=None):
        """Upravenie existujúceho komentára"""
        comment = self.get_object()
        comment.change_text(request.data['text'])
        comment.save()

        return Response("Komentár bol upravený.", status=status.HTTP_200_OK)


class ProblemViewSet(ModelViewSetWithSerializerContext):
    """
    Obsluhuje API endpoint pre Úlohy
    """
    class ProblemFilterSet(FilterSet):
        competition = Filter(
            field_name='series__semester__competition')
        semester = Filter(
            field_name='series__semester'
        )

        class Meta:
            model = Problem
            fields = ['order', 'series']

    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = (ProblemPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProblemFilterSet
    search_fields = ['text']
    ordering_fields = ['order', 'series__order', 'series__deadline']
    ordering = ['series__deadline', 'order']

    def perform_create(self, serializer):
        """
        Volá sa pri vytvarani objektu,
        checkuju sa tu permissions, ci user vie vytvorit problem v danej sutazi
        """
        series = serializer.validated_data['series']
        if series.can_user_modify(self.request.user):
            serializer.save()
        else:
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

    @action(methods=['get'], detail=True)
    def comments(self, request, pk=None):
        """Vráti komentáre (otázky) k úlohe"""
        comments_objects = self.get_object().get_comments(request.user)
        comments_serialized = map(
            (lambda obj: CommentSerializer(
                obj, context={'request': request}).data),
            comments_objects)
        return Response(comments_serialized, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path=r'add-comment',
            permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        """Pridá komentár (otázku) k úlohe"""
        problem: Problem = self.get_object()
        also_publish = problem.can_user_modify(request.user)

        problem.add_comment(request.data['text'], request.user, also_publish)
        alert_email = problem.series.semester.competition.alert_email
        emails_to_send = [
            ('Nový komentár',
             render_to_string('competition/emails/comment_added.txt',
                              context={
                                  'problem': problem,
                                  'comment': request.data['text']
                              }),
             None,
             [alert_email])
        ] if alert_email else []
        if also_publish:
            user_notification_email_text = render_to_string(
                'competition/emails/comment_added_to_problem.txt',
                context={
                    'problem': problem,
                    'from_staff': True,
                    'comment': request.data['text']
                })
            emails_to_send += [
                ('Nový komentár', user_notification_email_text,
                 None, [user.email])
                for user in problem.get_users_in_comment_thread() if user != request.user]
        send_mass_mail(emails_to_send)

        return Response("Komentár bol pridaný", status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminUser])
    def stats(self, request, pk=None):
        """Vráti štatistiky úlohy (histogram, počet riešiteľov...)"""
        return Response(self.get_object().get_stats())

    @action(methods=['post'], detail=True, url_name='upload-solution', url_path='upload-solution')
    def upload_solution(self, request, pk=None):
        """Nahrá užívateľské riešenie k úlohe"""
        problem: Problem = self.get_object()
        if not problem.series.can_submit:
            raise exceptions.ValidationError(
                detail='Túto úlohu už nie je možné odovzdať.')
        event_registration = EventRegistration.get_registration_by_profile_and_event(
            request.user.profile, problem.series.semester)

        if 'file' not in request.FILES:
            raise exceptions.ParseError(detail='Request neobsahoval súbor')

        file = request.FILES['file']

        if file.size > 20971520:  # 20 MB
            raise exceptions.ParseError(
                detail='Riešenie prekročilo maximálnu povolenú veľkosť',
            )

        if mime_type(file) != 'application/pdf':
            raise exceptions.ParseError(
                detail='Riešenie nie je vo formáte pdf')
        late_tag = problem.series.get_actual_late_flag()
        existing_solutions = Solution.objects.filter(
            problem=problem, semester_registration=event_registration)
        if len(existing_solutions) > 0 and late_tag is not None and not late_tag.can_resubmit:
            raise exceptions.ValidationError(
                detail='Túto úlohu už nie je možné odovzdať znova.')
        for solution in existing_solutions:
            solution.solution.delete()
        Solution.objects.filter(
            problem=problem, semester_registration=event_registration).delete()

        solution = Solution.objects.create(
            problem=problem,
            semester_registration=event_registration,
            late_tag=late_tag,
            is_online=True,
            solution=file
        )
        # solution.solution.save(
        #     solution.get_solution_file_name(), file, save=True)

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_name='upload-model-solution',
            url_path='upload-model-solution',  permission_classes=[IsAdminUser])
    def upload_model_solution(self, request, pk=None):
        """Nahrá užívateľské riešenie k úlohe"""
        problem: Problem = self.get_object()
        if 'file' not in request.FILES:
            raise exceptions.ParseError(detail='Request neobsahoval súbor')
        file = request.FILES['file']
        if mime_type(file) != 'application/pdf':
            raise exceptions.ParseError(
                detail='Riešenie nie je vo formáte pdf')
        problem.solution_pdf.save(
            f'vzorak-{problem.pk}.pdf', file, save=True
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, url_path='my-solution')
    def my_solution(self, request, pk=None):
        """Vráti riešenie k úlohe pre práve prihláseného užívateľa"""
        problem: Problem = self.get_object()
        event_registration = EventRegistration.get_registration_by_profile_and_event(
            request.user.profile, problem.series.semester)
        solution: Solution = Solution.objects.filter(
            problem=problem, semester_registration=event_registration).latest('uploaded_at')
        file = solution.solution
        if not file:
            raise exceptions.NotFound(
                detail='Zatiaľ nebolo nahraté žiadne riešenie')
        response = FileResponse(file, content_type='application/pdf')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    @action(detail=True, url_path='corrected-solution')
    def corrected_solution(self, request, pk=None):
        """Vráti opravené riešenie k úlohe pre práve prihláseného užívateľa"""
        problem: Problem = self.get_object()
        event_registration = EventRegistration.get_registration_by_profile_and_event(
            request.user.profile, problem.series.semester)
        solution: Solution = Solution.objects.filter(
            problem=problem, semester_registration=event_registration).latest('uploaded_at')
        file = solution.corrected_solution
        if not file:
            raise exceptions.NotFound(
                detail='Toto riešenie ešte nie je opravené')
        response = FileResponse(file, content_type='application/pdf')
        # Cache corrected solutions for 5 minutes.
        # - 'private' = cache only in user's browser, not in shared proxies
        # - 'max-age=300' = cache for 5 minutes (300 seconds)
        # - 'must-revalidate' = always check with server after cache expires
        # Corrected solutions change infrequently (only when admin re-uploads),
        # so short-term caching provides good balance between performance and freshness.
        response['Cache-Control'] = 'private, max-age=300, must-revalidate'
        return response

    @action(methods=['get'], detail=True, permission_classes=[IsAdminUser],
            url_path='download-solutions')
    def download_solutions(self, request, pk=None):
        """Vráti .zip archív všetkých užívateľských riešení k úlohe"""
        solutions = self.get_object().solution_set.all()
        # Open StringIO to grab in-memory ZIP contents
        stream = BytesIO()
        with zipfile.ZipFile(stream, 'w') as zipf:
            for solution in solutions:
                if solution.solution.name:
                    prefix = ''
                    if solution.late_tag is not None:
                        prefix = f'{solution.late_tag.slug}/'
                    file_name = solution.get_solution_file_name()
                    zipf.write(solution.solution.path,
                               f'{prefix}{file_name}')
        response = HttpResponse(stream.getvalue(),
                                content_type="application/x-zip-compressed")

        response['Content-Disposition'] = (
            'attachment; filename=export.zip'
        )

        return response

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser],
            url_path='upload-corrected')
    def upload_solutions_with_points(self, request, pk=None):
        """Nahrá .zip archív s opravenými riešeniami (pdf-kami)."""
        # pylint: disable=too-many-branches
        if 'file' not in request.data:
            raise exceptions.ParseError(detail='Žiaden súbor nebol pripojený')

        zfile = request.data['file']

        if not zipfile.is_zipfile(zfile):
            raise exceptions.ParseError(
                detail='Priložený súbor nie je zip')

        with zipfile.ZipFile(zfile) as zfile:
            if zfile.testzip():
                raise exceptions.ParseError(detail='Súbor zip je poškodený')

            parsed_filenames = []
            errors = []

            # TODO: checks file are really pdfs
            for filename in zfile.namelist():
                if not filename.endswith(".pdf"):
                    # Ignore other non-pdf files in the archive
                    continue

                if "__MACOSX" in filename:
                    # Ignore mac os metadata folder
                    continue

                try:
                    parts = filename.rstrip('.pdf').split('-')
                    score = int(parts[0])
                    problem_pk = int(parts[-2])
                    registration_pk = int(parts[-1])
                    event_reg = EventRegistration.objects.get(
                        pk=registration_pk)
                    solution = Solution.objects.get(semester_registration=event_reg,
                                                    problem=problem_pk)
                    validate_points(score)
                except ValidationError as exc:
                    errors.append({
                        'filename': filename,
                        'status': str(exc)
                    })
                except (IndexError, ValueError, AssertionError):
                    errors.append({
                        'filename': filename,
                        'status': 'Nedá sa prečítať názov súboru. Skontroluj, že názov súboru'
                        'je v tvare BODY-MENO-ID_ULOHY-ID_REGISTRACIE_USERA.pdf'
                    })
                    continue
                except EventRegistration.DoesNotExist:
                    errors.append({
                        'filename': filename,
                        'status': f'Registrácia používateľa s id {registration_pk} neexistuje'
                    })
                    continue
                except Solution.DoesNotExist:
                    errors.append({
                        'filename': filename,
                        'status': f'Riešenie pre registráciu používateľa s id {registration_pk}'
                        f'a úlohy id {problem_pk} neexistuje'
                    })
                    continue

                parsed_filenames.append((filename, score, solution))

            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            for filename, score, solution in parsed_filenames:
                with zfile.open(filename) as corrected_solution:
                    solution.score = score
                    solution.corrected_solution = File(corrected_solution)

                    try:
                        solution.full_clean()
                        solution.save()
                    except CoreValidationError:
                        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            return Response()


class ProblemAdministrationViewSet(ModelViewSetWithSerializerContext):
    queryset = Problem.objects.all()
    serializer_class = ProblemWithSolutionsSerializer
    permission_classes = (IsAdminUser,)

    @action(methods=['post'], detail=True, url_path='upload-points')
    def upload_points(self, request, pk=None):
        problem = self.get_object()
        solutions = request.data['solution_set']
        for solution_dict in solutions:
            solution = Solution.objects.get(pk=solution_dict['id'])
            if solution.problem != problem:
                continue
            solution.score = solution_dict['score']
            try:
                solution.full_clean()
                solution.save()
            except CoreValidationError:
                return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(status=status.HTTP_200_OK)


class SeriesViewSet(ModelViewSetWithSerializerContext):
    """
    Obsluhuje API endpoint pre Úlohy
    """
    class SeriesFilterSet(FilterSet):
        competition = Filter(
            field_name='semester__competition')

        class Meta:
            model = Series
            fields = ['order', 'semester']

    queryset = Series.objects.all()
    serializer_class = SeriesWithProblemsSerializer
    permission_classes = (CompetitionRestrictedPermission,)
    http_method_names = ['get', 'head', 'put', 'patch', "post"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = SeriesFilterSet
    search_fields = ['semester__competition__name', 'semester__year']
    ordering_fields = ['deadline']
    ordering = ['-deadline']

    def perform_create(self, serializer):
        """
        Vola sa pri vytvarani objektu,
        checkuju sa tu permissions, ci user vie vytvorit semester v danej sutazi
        """
        if Series.can_user_create(self.request.user, serializer.validated_data):
            serializer.save()
        else:
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

    @action(methods=['get'], detail=True)
    def results(self, request: Request, pk: Optional[int] = None):
        """Vráti výsledkovku pre sériu"""
        series = self.get_object()
        if series.frozen_results is not None:
            return Response(json.loads(series.frozen_results), status=status.HTTP_200_OK)
        results = series_results(series)
        return Response(results, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='results/freeze')
    def freeze_results(self, request: Request, pk: Optional[int] = None):
        series: Series = self.get_object()
        try:
            freeze_series_results(series)
        except FreezingNotClosedResults as exc:
            raise exceptions.MethodNotAllowed(
                method='series/results/freeze',
                detail='Séria nemá opravené všetky úlohy a teda sa nedá uzavrieť.') from exc
        except UserHasInvalidSchool as exc:
            raise exceptions.MethodNotAllowed(
                method='series/results/freeze',
                detail=str(exc)) from exc
        try:
            freeze_semester_results(series.semester)
        except FreezingNotClosedResults:
            pass
        return Response('Séria bola uzavretá', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='results/unfreeze')
    def unfreeze_results(self, request: Request, pk: Optional[int] = None):
        series: Series = self.get_object()
        series.unfreeze_results()
        series.semester.unfreeze_results()
        return Response('Séria bola znovu otvorená', status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def stats(self, request, pk=None):
        """Vráti štatistiky (histogramy, počty riešiteľov) všetkých úloh v sérií"""
        problems = self.get_object().problems
        stats = []
        for problem in problems:
            stats.append(problem.get_stats())
        return Response(stats, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path=r'current/(?P<competition_id>\d+)')
    def current(self, request, competition_id=None):
        """Vráti aktuálnu sériu"""
        current_semester_series = Semester.objects.filter(
            competition=competition_id
        ).current().series_set
        current_series = current_semester_series.order_by('deadline')
        current_series = next(
            filter(lambda s: s.can_submit, current_series), None)
        if current_series is None:
            current_series = current_semester_series.order_by(
                '-deadline').first()
        serializer = SeriesWithProblemsSerializer(
            current_series, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='sum-methods')
    def sum_methods(self, request, limit=None, offset=None):
        sum_methods = [{'id': sum_method_tuple[0], 'name': sum_method_tuple[1]}
                       for sum_method_tuple in SERIES_SUM_METHODS]
        count = len(sum_methods)

        limit = request.query_params.get(
            'limit', None)
        offset = request.query_params.get(
            'offset', None)

        if limit is None and offset is None:
            return Response(
                sum_methods,
                status=status.HTTP_200_OK
            )
        try:
            limit = 20 if limit is None else int(limit)
            offset = 0 if offset is None else int(offset)
        except ValueError:
            return Response(
                {"detail": "Invalid limit or offset"},
                status=status.HTTP_400_BAD_REQUEST
            )
        url = self.request.build_absolute_uri()
        return Response(
            {
                "count": count,
                "next": replace_query_param(
                    url, 'offset', min(offset+limit, count)
                ) if min(offset+limit, count) != offset else None,
                "previous": replace_query_param(
                    url, 'offset', max(0, offset-limit)
                ) if max(offset-limit, 0) != offset else None,
                "results": sum_methods[min(offset, count):min(offset+limit, count)]
            }
        )


class SolutionViewSet(viewsets.ModelViewSet):
    """Užívateľské riešenia"""
    class SolutionFilterSet(FilterSet):
        profile = Filter(
            field_name='semester_registration__profile'
        )
        school = profile = Filter(
            field_name='semester_registration__school'
        )
        missing_file = Filter(
            'solution__isnull'
        )
        missing_corrected_file = Filter(
            'corrected_solution__isnull'
        )
        uploaded_after = Filter(
            'uploaded_at__gt'
        )
        uploaded_before = Filter(
            'uploaded_at__lt'
        )

        class Meta:
            model = Solution
            fields = ['problem', 'late_tag', 'semester_registration']
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['semester_registration__profile__first_name',
                     'semester_registration__profile__last_name']
    ordering_fields = ['problem', 'score', 'uploaded_at']
    ordering = ['uploaded_at']

    @action(methods=['post'], detail=True, url_path='add-positive-vote',
            permission_classes=[IsAdminUser])
    def add_positive_vote(self, request, pk=None):
        """Pridá riešeniu kladný hlas"""
        self.get_object().set_vote(Vote.POSITIVE)
        return Response('Pridaný pozitívny hlas.', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='add-negative-vote',
            permission_classes=[IsAdminUser])
    def add_negative_vote(self, request, pk=None):
        """Pridá riešeniu negatívny hlas"""
        self.get_object().set_vote(Vote.NEGATIVE)
        return Response('Pridaný negatívny hlas.', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='remove-vote',
            permission_classes=[IsAdminUser])
    def remove_vote(self, request, pk=None):
        """Odoberie riešeniu hlas"""
        self.get_object().set_vote(Vote.NONE)
        return Response('Hlas Odobraný.', status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='file-solution',
            permission_classes=[ProblemPermission])
    def file_solution(self, request, pk=None):
        """Stiahne riešenie"""
        solution = self.get_object()
        file = solution.solution
        if not file:
            raise exceptions.NotFound(
                detail='Zatiaľ nebolo nahraté žiadne riešenie')
        return FileResponse(
            file, content_type='application/pdf',
        )

    @action(methods=['get'], detail=True, url_path='file-corrected',
            permission_classes=[ProblemPermission])
    def file_corrected(self, request, pk=None):
        """Stiahne opravenú verziu riešenia"""
        solution = self.get_object()
        file = solution.corrected_solution
        if not file:
            raise exceptions.NotFound(
                detail='Zatiaľ nebolo nahraté žiadne riešenie')
        return FileResponse(
            file, content_type='application/pdf',
        )

    @action(methods=['post'], detail=True,
            url_path='upload-solution-file',
            permission_classes=[ProblemPermission])
    def upload_solution_file(self, request, pk=None):
        solution: Solution = self.get_object()
        if 'file' not in request.FILES:
            raise exceptions.ParseError(detail='Request neobsahoval súbor')

        file = request.FILES['file']
        if mime_type(file) != 'application/pdf':
            raise exceptions.ParseError(
                detail='Riešenie nie je vo formáte pdf')
        solution.solution.save(
            solution.get_solution_file_path(), file, save=True
        )
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True,
            url_path='upload-corrected-solution-file',
            permission_classes=[ProblemPermission])
    def upload_corrected_solution_file(self, request, pk=None):
        solution: Solution = self.get_object()
        if 'file' not in request.FILES:
            raise exceptions.ParseError(detail='Request neobsahoval súbor')

        file = request.FILES['file']
        if mime_type(file) != 'application/pdf':
            raise exceptions.ParseError(
                detail='Riešenie nie je vo formáte pdf')
        solution.corrected_solution.save(
            solution.get_corrected_solution_file_path(), file, save=True
        )
        return Response(status=status.HTTP_201_CREATED)


class SemesterListViewSet(viewsets.ReadOnlyModelViewSet):
    """Zoznam semestrov (iba základné informácie)"""
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = (CompetitionRestrictedPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    http_method_names = ['get', 'post', 'head']
    filterset_fields = ['competition']
    ordering = ['-start']
    search_fields = ['competition__name', 'year']
    ordering_fields = ['start', 'end', 'year']


class SemesterViewSet(ModelViewSetWithSerializerContext):
    """Semestre - aj so sériami a problémami"""
    queryset = Semester.objects.all()
    serializer_class = SemesterWithProblemsSerializer
    permission_classes = (CompetitionRestrictedPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_year',
                        'season_code', 'competition']
    search_fields = ['competition__name', 'year', 'school_year']
    ordering_fields = ['start', 'end', 'year']
    ordering = ['-start']
    http_method_names = ['get', 'head', 'put', 'patch', 'post']

    def perform_create(self, serializer):
        """
        Vola sa pri vytvarani objektu,
        checkuju sa tu permissions, ci user vie vytvorit semester v danej sutazi
        """
        competition = serializer.validated_data['competition']
        if competition.can_user_modify(self.request.user):
            serializer.save()
        else:
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

    @action(methods=['post'], detail=True, url_path='results/freeze')
    def freeze_results(self, request: Request, pk: Optional[int] = None):
        semester: Semester = self.get_object()
        try:
            freeze_semester_results(semester)
        except FreezingNotClosedResults as exc:
            raise exceptions.MethodNotAllowed(
                method='series/results/freeze',
                detail='Semester nemá uzavreté všetky série a teda sa nedá uzavrieť.') from exc
        return Response('Semester bol uzavretý', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='results/unfreeze')
    def unfreeze_results(self, request: Request, pk: Optional[int] = None):
        semester: Semester = self.get_object()
        semester.unfreeze_results()
        return Response('Semester bol znova otvorený', status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def results(self, request, pk=None):
        """Vráti výsledkovku semestra"""
        semester = self.get_object()
        current_results = semester_results(semester)
        return Response(current_results, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminUser])
    def schools(self, request, pk=None):
        """Vráti školy, ktorých žiaci boli zapojený do semestra"""
        schools = School.objects.filter(eventregistration__event=pk)\
            .distinct()\
            .order_by('city', 'street')
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True,
            url_path='offline-schools', permission_classes=[IsAdminUser])
    def offline_schools(self, request, pk=None):
        """Vráti školy, ktorých aspoň nejaký žiaci odovzdali papierové riešenia"""
        schools = School.objects.filter(eventregistration__event=pk)\
            .filter(eventregistration__solution__is_online=False)\
            .distinct()\
            .order_by('city', 'street')
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True,
            url_path=r'invitations/(?P<num_participants>\d+)/(?P<num_substitutes>\d+)',
            permission_classes=[IsAdminUser])
    def invitations(self, request, pk=None, num_participants=32, num_substitutes=20):
        """Vráti TeXovský kus zdrojáku pre výrobu pozvánky na sústredenie pre účastníka"""
        semester = self.get_object()
        num_participants = int(num_participants)
        num_substitutes = int(num_substitutes)
        participants = generate_praticipant_invitations(
            semester_results(semester),
            num_participants,
            num_substitutes
        )
        participants.sort(key=itemgetter('first_name'))
        participants.sort(key=itemgetter('last_name'))

        return Response(participants, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True,
            url_path=r'school-invitations/(?P<num_participants>\d+)/(?P<num_substitutes>\d+)',
            permission_classes=[IsAdminUser])
    def school_invitations(self, request, pk=None, num_participants=32, num_substitutes=20):
        """Vráti TeXovský kus zdrojáku pre výrobu pozvánky na sústredenie pre školu"""
        num_participants = int(num_participants)
        num_substitutes = int(num_substitutes)
        semester = self.get_object()
        participants = generate_praticipant_invitations(
            semester_results(semester),
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

    @action(methods=['get'], detail=False, url_path=r'current/(?P<competition_id>\d+)')
    def current(self, request, competition_id=None):
        """Vráti aktuálny semester"""
        current_semester = self.get_queryset().filter(
            competition=competition_id).current()
        serializer = SemesterWithProblemsSerializer(
            current_semester, many=False)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path=r'current-results/(?P<competition_id>\d+)')
    def current_results(self, request, competition_id=None):
        """Vráti výsledky pre aktuálny semester"""
        current_semester = self.get_queryset().filter(
            competition=competition_id).current()
        current_results = semester_results(current_semester)
        return Response(current_results, status=status.HTTP_201_CREATED)

    def __get_participants(self):
        semester = self.get_object()
        participants_id = []

        for series in semester.series_set.all():
            solutions = Solution.objects.only('semester_registration')\
                .filter(problem__series=series)\
                .order_by('semester_registration')

            for solution in solutions:
                participants_id.append(
                    solution.semester_registration.profile.pk)

        profiles = Profile.objects.only("user").filter(pk__in=participants_id)
        serializer = ProfileExportSerializer(profiles, many=True)
        return serializer

    @action(methods=['get'], detail=True)
    def participants(self, request, pk=None):
        """Vráti všetkých užívateľov zapojených do semestra"""
        serializer = self.__get_participants()
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='participants-export')
    def participants_export(self, request, pk=None):
        """Vráti všetkých užívateľov zapojených do semestra"""
        serializer = self.__get_participants()
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        header = ProfileExportSerializer.Meta.fields
        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        writer.writerows(serializer.data)
        return response

    def post(self, request, format_post):
        """Založí nový semester"""
        serializer = SemesterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(ModelViewSetWithSerializerContext):
    """Ročníky akcií (napríklad Matboj 2021)"""
    class EventFilterSet(FilterSet):

        class SuitableForGradeFilter(ModelChoiceFilter):
            def filter(self, qs: BaseManager, value: Grade):
                if value is None:
                    return qs
                return qs.filter(
                    competition__min_years_until_graduation__lte=value.years_until_graduation
                )

        grade = SuitableForGradeFilter(queryset=Grade.objects.all())
        future = UpcomingFilter(field_name='end')

        class Meta:
            model = Event
            fields = ['school_year',
                      'season_code', 'location', 'competition']

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (CompetitionRestrictedPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilterSet
    search_fields = ['competition__name', 'year', 'additional_name']
    ordering_fields = ['start', 'end', 'year']
    ordering = ['-start']

    def perform_create(self, serializer):
        """
        Vola sa pri vytvarani objektu,
        checkuju sa tu permissions, ci user vie vytvorit event v danej sutazi
        """
        if Event.can_user_create(self.request.user, serializer.validated_data):
            serializer.save()
        else:
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """Registruje prihláseného užívateľa na akciu"""
        event: Event = self.get_object()
        profile = request.user.profile
        if not event.is_active:
            raise ValidationError('Súťaž aktuálne neprebieha.')
        if not event.can_user_participate(request.user):
            raise ValidationError(
                'Používateľa nie je možné registrovať - Zlá veková kategória')
        if EventRegistration.get_registration_by_profile_and_event(
                profile, event):
            raise ValidationError('Používateľ je už zaregistrovaný')
        EventRegistration.objects.create(
            event=event,
            school=profile.school,
            profile=profile,
            grade=Grade.get_grade_by_year_of_graduation(
                profile.year_of_graduation),
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='can-participate'
    )
    def can_participate(self, request, pk=None):
        event = self.get_object()
        return Response(
            {'can-participate': event.can_user_participate(request.user)},
            status=status.HTTP_200_OK
        )

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated])
    def participants(self, request, pk=None):
        event = self.get_object()
        # Profile serializer
        return event.registered_profiles()

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def active(self, request):
        """Get all active events"""
        active_events = self.get_queryset().active()
        serializer = self.serializer_class(active_events, many=True)
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """Registrácie na akcie"""

    class EventRegistrationFilterSet(FilterSet):

        class SuitableForProblemFilter(ModelChoiceFilter):
            def filter(self, qs: BaseManager, value: Problem):
                if value is None:
                    return qs

                return qs.filter(
                    event=value.series.semester
                )

        problem = SuitableForProblemFilter(queryset=Problem.objects.all())
        future = UpcomingFilter(field_name='end')

        class Meta:
            model = EventRegistration
            fields = ['school',
                      'profile', 'grade', 'event']

    queryset = EventRegistration.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventRegistrationFilterSet
    search_fields = ['profile__first_name', 'profile__last_name']
    ordering_fields = ['event__start']
    ordering = ['event__start']
    permission_classes = (CompetitionRestrictedPermission,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EventRegistrationReadSerializer
        return EventRegistrationWriteSerializer

    def perform_create(self, serializer):
        if not EventRegistration.can_user_create(self.request.user, serializer.validated_data):
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

        return super().perform_create(serializer)


class PublicationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PublicationType.objects.all()
    serializer_class = PublicationTypeSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    """Publikácie(výsledky, brožúrky, časopisy, ...)"""
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = (CompetitionRestrictedPermission,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publication_type',
                        'event', 'order']
    search_fields = ['name', 'order', 'publication_type']
    ordering_fields = ['name', 'order', 'publication_type']

    def perform_create(self, serializer):
        '''
        Vola sa pri vytvarani objektu,
        checkuju sa tu permissions, ci user vie vytvorit publication v danom evente
        '''
        self._ensure_file_attached(serializer)

        if Publication.can_user_create(self.request.user, serializer.validated_data):
            serializer.save()
        else:
            raise exceptions.PermissionDenied(
                'Nedostatočné práva na vytvorenie tohoto objektu')

    def perform_update(self, serializer):
        if not serializer.partial:
            self._ensure_file_attached(serializer)

        return super().perform_update(serializer)

    @staticmethod
    def _ensure_file_attached(serializer: PublicationSerializer):
        if 'file' not in serializer.validated_data:
            raise exceptions.ValidationError(
                'Publikácia musí mať pripojený súbor'
            )


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    """Ročníky riešiteľov (Z9,S1 ...)"""
    queryset = Grade.objects.filter(is_active=True).all()
    serializer_class = GradeSerializer


class LateTagViewSet(viewsets.ReadOnlyModelViewSet):
    """Omeškania"""
    queryset = LateTag.objects.all()
    serializer_class = LateTagSerializer
