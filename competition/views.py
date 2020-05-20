from django.contrib import messages
from django.views.generic import DetailView, ListView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from competition.forms import SeriesSolutionForm
from competition.models import (Competition, EventRegistration, Grade, LateTag, Problem,
                                Semester, Series, Solution)

from competition.utils import generate_praticipant_invitations, get_school_year_by_date, SERIES_SUM_METHODS
from operator import itemgetter
import json
import datetime
from operator import itemgetter


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
        context['problems'] = zip(self.object.problem_set.all(), form)
        return context

    def post(self, request, **kwargs):
        # pylint: disable=unused-argument
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
        for problem in self.object.problem_set.all():
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
    template_name = 'competition/invitations_latex.html'

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
        # pylint: disable=unused-argument
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


def validate_load_semester_input(input):
    return True


def load_semester_data(request):
    if not request.user.is_staff:
        return HttpResponse('Toto nie je pre tvoje oči')

    if request.method == 'POST':
        semester_data = json.loads(request.body)

        # Checks
        if not validate_load_semester_input(semester_data):
            return HttpResponse('Nesprávny vstup')

        # Create semester
        sem_start = datetime.datetime.strptime(
            semester_data['semester_start'], '%Y-%m-%dT%H:%M:%S.%fZ')
        sem_end = datetime.datetime.strptime(
            semester_data['semester_end'], '%Y-%m-%dT%H:%M:%S.%fZ')
        mid_semester = sem_start + (sem_end - sem_start)/2
        season_code = Semester.SEASON_CHOICES[semester_data['season']]
        school_year = get_school_year_by_date(date=mid_semester)
        competition = Competition.objects.get(pk=semester_data['seminar'])
        new_semester = Semester.objects.create(
            competition=competition,
            year=semester_data['year'],
            school_year=school_year,
            start=semester_data['semester_start'],
            end=semester_data['semester_end'],
            season_code=semester_data['season']
        )

        # Add late tags
        for late_tag_id in semester_data['late_tags']:
            late_tag = LateTag.objects.get(pk=late_tag_id)
            new_semester.late_tags.add(late_tag)
        new_semester.save()

        # Create Series
        for s in semester_data['series']:
            new_series = Series.objects.create(
                semester=new_semester,
                order=s['order'],
                deadline=s['deadline'],
                complete=False,
                sum_method=s['sum_method']
            )

            # Create problems
            for problem in s['problems']:
                Problem.objects.create(
                    text=problem['text'],
                    order=problem['order'],
                    series=new_series
                )
        return HttpResponse('OK')
    else:
        # GET response - form
        context = {}

        # Semestre
        context['seminars'] = Competition.objects.filter(
            competition_type=0).all()
        context['late_tags'] = LateTag.objects.all()
        context['season_choices'] = Semester.SEASON_CHOICES
        context['sum_methods'] = SERIES_SUM_METHODS
        context['seminar_defaults'] = {}
        for seminar in context['seminars']:
            semester = Semester.objects.filter(
                competition=seminar).order_by('-end').first()
            if not semester:
                continue
            if semester.season_code == 0:
                year = semester.year
            else:
                year = semester.year + 1
            context['seminar_defaults'][seminar] = {
                'year': year,
                'late_tags': semester.late_tags.all(),
                'sum_method': semester.series_set.first().sum_method
            }
        # Vyber posledné nastavenia súťaží
        return render(request, template_name='competition/semester_load.html', context={'json_data': context})
