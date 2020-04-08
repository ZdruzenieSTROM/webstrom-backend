from django.shortcuts import render
from django.views.generic.detail import DetailView
from competition.models import Semester, Series, Problem

# Create your views here.
class SemesterProblemsView(DetailView):
    template_name = 'competition/semester_problems.html'
    model = Semester

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semester'] = self.object
        context['series'] = Series.objects.filter(
            semester=self.object
        )
        for serie in context['series']:

            context['problems'][serie.pk] = Problem.objects.filter(
                serie=serie
            ).order_by('order')


class LatestSemesterView(SemesterProblemsView):
    def get_object():
        pass
