from django.views.generic.detail import DetailView

from competition.models import Competition, Semester, Series


class SemesterProblemsView(DetailView):
    template_name = 'semester_problems.html'
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
