from json import dumps as json_dumps
from json import loads as json_loads
from operator import itemgetter

from django.utils.timezone import now

from competition.models import EventRegistration, Semester, Series
from competition.serializers import EventRegistrationReadSerializer
from competition.utils import sum_methods


class FreezingNotClosedResults(Exception):
    """Snažíš sa zamraziť výsledky série, ktorá nemá opravené všetky riešenia"""


def semester_results(self: Semester) -> dict:
    """Vyrobí výsledky semestra"""
    if self.frozen_results is not None:
        return json_loads(self.frozen_results)
    results = []
    for registration in self.eventregistration_set.all():
        if registration.has_solutions():
            results.append(_generate_result_row(registration, self))

    results.sort(key=itemgetter('total'), reverse=True)
    results = _rank_results(results)
    return results


def freeze_semester_results(semester: Semester):
    if any(not series.complete for series in semester.series_set.all()):
        raise FreezingNotClosedResults()

    semester.frozen_results = json_dumps(semester_results(semester))
    semester.save()


def series_results(series: Series):
    results = [
        _generate_result_row(registration, only_series=series)
        for registration in series.semester.eventregistration_set.all()
        if registration.has_solutions()
    ]

    results.sort(key=itemgetter('total'), reverse=True)

    return _rank_results(results)


def freeze_series_results(series: Series):
    if any(
        problem.num_solutions != problem.num_corrected_solutions
        for problem in series.problems.all()
    ) or series.deadline > now():
        raise FreezingNotClosedResults()

    series.frozen_results = json_dumps(series_results(series))
    series.save()


def generate_praticipant_invitations(
        results_with_ranking: list[dict],
        number_of_participants: int,
        number_of_substitues: int,
) -> list[dict]:
    invited_users = []
    for i, result_row in enumerate(results_with_ranking):
        if i < number_of_participants:
            invited_users.append({
                'first_name': result_row['registration']['profile']['first_name'],
                'last_name': result_row['registration']['profile']['last_name'],
                'school': result_row['registration']['school'],
                'is_participant': True
            })
        elif i < number_of_participants+number_of_substitues:
            invited_users.append({
                'first_name': result_row['registration']['profile']['first_name'],
                'last_name': result_row['registration']['profile']['last_name'],
                'school': result_row['registration']['school'],
                'is_participant': False
            })
    return invited_users


def _generate_result_row(
    semester_registration: EventRegistration,
    semester: Semester | None = None,
    only_series: Series | None = None,
):
    """
    Vygeneruje riadok výsledku pre používateľa.
    Ak je uvedený only_semester vygenerujú sa výsledky iba sa daný semester
    """
    user_solutions = semester_registration.solution_set
    series_set = semester.series_set.order_by(
        'order') if semester is not None else [only_series]
    solutions = []
    subtotal = []
    for series in series_set:
        series_solutions = []
        solution_points = []
        for problem in series.problems.order_by('order'):
            sol = user_solutions.filter(problem=problem).first()

            solution_points.append(sol.score or 0 if sol is not None else 0)
            series_solutions.append(
                {
                    'points': (str(sol.score if sol.score is not None else '?')
                               if sol is not None else '-'),
                    'solution_pk': sol.pk if sol is not None else None,
                    'problem_pk': problem.pk,
                    'votes': 0  # TODO: Implement votes sol.vote
                }
            )
        series_sum_func = getattr(sum_methods, series.sum_method or '',
                                  sum_methods.series_simple_sum)
        solutions.append(series_solutions)
        subtotal.append(
            series_sum_func(solution_points, semester_registration)
        )
    return {
        # Poradie - horná hranica, v prípade deleného miesto(napr. 1.-3.) ide o nižšie miesto(1)
        'rank_start': 0,
        # Poradie - dolná hranica, v prípade deleného miesto(napr. 1.-3.) ide o vyššie miesto(3)
        'rank_end': 0,
        # Indikuje či sa zmenilo poradie od minulej priečky, slúži na delené miesta
        'rank_changed': True,
        # primary key riešiteľovej registrácie do semestra
        'registration': EventRegistrationReadSerializer(semester_registration).data,
        # Súčty bodov po sériách
        'subtotal': subtotal,
        # Celkový súčet za danú entitu
        'total': sum(subtotal),
        # Zoznam riešení,
        'solutions': solutions
    }


def _rank_results(results: list[dict]) -> list[dict]:
    # Spodná hranica
    current_rank = 1
    n_teams = 1
    last_points = None
    for res in results:
        if last_points != res['total']:
            current_rank = n_teams
            last_points = res['total']
            res['rank_changed'] = True
        else:
            res['rank_changed'] = False
        res['rank_start'] = current_rank
        n_teams += 1

    # Horná hranica
    current_rank = len(results)
    n_teams = len(results)
    last_points = None
    for res in reversed(results):
        if last_points != res['total']:
            current_rank = n_teams
            last_points = res['total']
        res['rank_end'] = current_rank
        n_teams -= 1
    return results
