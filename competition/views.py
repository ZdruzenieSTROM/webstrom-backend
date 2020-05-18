from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, View

from competition.forms import SeriesSolutionForm
from competition.models import (Competition, EventRegistration, Grade,
                                Problem, Semester, Series, Solution)


class SeriesProblemsView(DetailView):
    template_name = 'competition/series.html'
    model = Series

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['registration'] = EventRegistration.objects.filter(
                event=self.object.semester,
                profile=self.request.user.profile)
        except AttributeError:
           context['registration']  = None

        context['form'] = form = SeriesSolutionForm(self.object)
        context['problems'] = zip(self.object.problem_set.all(), form)
        return context

    def post(self, request, **kwargs):
        form = SeriesSolutionForm(
            self.get_object(),
            data=request.POST,
            files=request.FILES)

        try:
            registration = EventRegistration.objects.get(
                event=self.get_object().semester,
                profile=self.request.user.profile)
            assert form.is_valid()
        except AttributeError:
            messages.error(request, 'Na odovzdávanie riešení je potrebné byť prihlásený')
        except (EventRegistration.DoesNotExist, AssertionError):
            messages.error(request, 'Odovzdávanie riešení zlyhalo')
        else:
            for field in form.fields:
                if field in request.FILES:
                    problem = Problem.objects.get(pk=int(field))
                    try:
                        solution = Solution.objects.get(
                            semester_registration=registration,
                            problem=problem)
                        messages.debug(request, 'Riešenie existovalo')
                    except Solution.DoesNotExist:
                        solution = Solution(
                            semester_registration=registration,
                            problem=problem)
                        messages.debug(request, 'Riešenie neexistovalo')
                    
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
            try:
                years[sem.year]
            except KeyError:
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
        return context


class SemesterResultsLatexView(SemesterResultsView):
    template_name = 'competition/results_latex.html'


class SemesterRegistrationView(View):
    def get(self, request, pk, series, **kwargs):
        try:
            profile = self.request.user.profile
            semester = Semester.objects.get(pk=pk)
            assert not EventRegistration.objects.filter(profile=profile, event=semester)
            EventRegistration(
                profile=profile, school=profile.school,
                grade=Grade.get_grade_by_year_of_graduation(profile.year_of_graduation),
                event=semester).save()
        except AssertionError:
            messages.info(request, 'Do tohto semestra už si zaregistrovaný')
        except AttributeError:
            messages.error(request, 'Na odovzdávanie riešení je potrebné byť prihlásený')
        else:
            messages.success(
                request,
                f'{Semester.objects.get(pk=pk)}: Registrácia do semestra prebehla úspešne')
        
        return redirect('competition:series-problems-detail', pk=series)
