from operator import itemgetter

from django.views.generic import DetailView, ListView

from competition.models import Competition, Semester, Series
from competition.utils import generate_praticipant_invitations


class SeriesProblemsView(DetailView):
    template_name = 'competition/series.html'
    model = Series


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

        context['results'] = self.object.results_with_ranking()
        context['results_type'] = 'series'
        return context


class SemesterResultsView(DetailView):
    model = Semester
    template_name = 'competition/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    context_object_name = 'semester'
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


class SemesterPublicationView(DetailView):
    model = Semester
    template_name = 'competition/publication.html'
