from operator import itemgetter

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, View

from competition.forms import SeriesSolutionForm
from competition.models import (Competition, EventRegistration, Grade, Problem,
                                Semester, Series, Solution)
from competition.utils import generate_praticipant_invitations


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
