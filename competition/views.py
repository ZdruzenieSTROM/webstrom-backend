from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from competition.models import Competition, LateTag, Semester, Series, Problem
from competition.utils import generate_praticipant_invitations, get_school_year_by_date
from operator import itemgetter
import json
import datetime


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
        context['schools_offline'] = self.object.semester.get_schools(offline_users_only=True)
        return context


class SemesterResultsLatexView(SemesterResultsView):
    template_name = 'competition/results_latex.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schools'] = self.object.get_schools()
        context['schools_offline'] = self.object.get_schools(offline_users_only=True)
        return context

class SemesterInvitationsLatexView(DetailView):
    model = Semester
    context_object_name = 'semester'
    template_name = 'competition/invitations_latex.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        participants = generate_praticipant_invitations(
            self.object.results_with_ranking(),
            self.kwargs.get('num_participants',32),
            self.kwargs.get('num_substitutes',20),
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


def validate_load_semester_input(input):
    return True

def load_semester_data(request):
    if not request.user.is_staff:
        return HttpResponse('Toto nie je pre tvoje oči')

    if request.method == 'GET':
        #semester_data = json.loads(request.body)
        with open('sem.json', 'r',encoding='utf-8') as f:
            semester_data = json.load(f)

        # Checks
        if not validate_load_semester_input(semester_data):
            return HttpResponse('Nesprávny vstup')

        # Create semester
        sem_start = datetime.datetime.strptime(semester_data['semester_start'], '%Y-%m-%dT%H:%M:%S.%fZ')
        sem_end = datetime.datetime.strptime(semester_data['semester_end'], '%Y-%m-%dT%H:%M:%S.%fZ')
        mid_semester =  sem_start + (sem_end - sem_start)/2
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

            #Create problems
            for problem in s['problems']:
                Problem.objects.create(
                    text=problem['text'],
                    order=problem['order'],
                    series=new_series
                )
        return HttpResponse('OK')
    else:
        # GET response - form
        # Vyber posledné nastavenia súťaží
        return HttpResponse('Toto nie je pre tvoje očhi')
