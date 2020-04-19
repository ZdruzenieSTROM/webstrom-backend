from django.views.generic import DetailView, ListView

from competition.models import Competition, Semester, Series


class SemesterProblemsView(DetailView):
    template_name = 'competition/semester_problems.html'
    model = Semester

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semester'] = self.object
        context['series'] = Series.objects.filter(
            semester=self.object)
        context['problems'] = {}

        for series in context['series']:
            context['problems'][series.pk] = series.problem_set.order_by(
                'order')

        context['competition_semesters'] = self.object.competition.semester_set.all()

        return context


class LatestSemesterView(SemesterProblemsView):
    def get_object(self):
        return Competition.get_by_current_site().semester_set.order_by('-end').first()


class SeriesProblemsView(DetailView):
    template_name = 'competition/series_problems.html'
    model = Series

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['series'] = self.object
        context['problems'] = {}
        context['problems'] = self.object.problem_set.order_by('order')

        return context


class ArchiveView(ListView):
    template_name = 'competition/archive.html'
    model = Semester
    context_object_name = 'context'

    def get_queryset(self):
        site_competition = Competition.get_by_current_site()
        years = {}
        for sem in Semester.objects.filter(competition=site_competition).order_by('-year'):
            try:
                years[sem.year]
            except KeyError:
                years[sem.year] = []
            years[sem.year].append(sem)
            pass
        return years


class SemesterDetailView(DetailView):
    template_name = 'competition/semester_detail.html'
    model = Semester

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semester'] = self.object
        context['series'] = Series.objects.filter(
            semester=self.object)
        context['competition_semesters'] = self.object.competition.semester_set.all()

        return context
