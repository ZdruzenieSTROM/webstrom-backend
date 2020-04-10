from django.shortcuts import render
from django.views.generic.detail import DetailView
from competition.models import Semester, Serie, Problem

# Create your views here.
class SemesterProblemsView(DetailView):
    template_name = 'semester_problems.html'
    model = Semester

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semester'] = self.object
        context['series'] = Serie.objects.filter(
            semester=self.object
        )
        context['problems'] = {}
        
        for serie in context['series']:
            context['problems'][serie.pk] = Problem.objects.filter(
                serie=serie
            ).order_by('order')

        return context


class LatestSemesterView(SemesterProblemsView):
    def get_object():
        pass
