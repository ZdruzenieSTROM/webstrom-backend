from django.utils.timezone import now


def get_school_year_start_by_date(date=None) -> int:
    if date is None:
        date = now()

    return date.year if date.month >= 9 else date.year - 1


def get_school_year_end_by_date(date=None) -> int:
    return get_school_year_start_by_date(date) + 1


def get_school_year_by_date(date=None) -> str:
    return f'{get_school_year_start_by_date(date)}/{get_school_year_end_by_date(date)}'


def rank_results(results):
    # Spodná hranica
    current_rank = 1
    n_teams = 1
    last_points = None
    for res in results:
        if last_points != res['total']:
            current_rank = n_teams
            last_points = res['total']
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
            res['rank_changed'] = True
        else:
            res['rank_changed'] = False
        res['rank_end'] = current_rank
        n_teams -= 1
    return results


# Súčtové metódy pre semináre


def dot_product(solutions, weights):
    return sum([s*w for s, w in zip(solutions, weights)])


def solutions_to_list_of_points(solutions):
    return [s.score or 0 if s is not None else 0 for s in solutions]


def solutions_to_list_of_points_pretty(solutions):
    return [str(s.score or '?') if s is not None else '-' for s in solutions]


def series_simple_sum(solutions, user_registration=None):
    return sum([s.score or 0 for s in solutions if s is not None])


def series_general_weighted_sum(solutions, weights):
    if weights:
        points = solutions_to_list_of_points(solutions)
        points.sort(reverse=True)
        return dot_product(points, weights)
    else:
        return series_simple_sum(solutions)


def series_Malynar_sum(solutions, user_registration):
    weights = None
    if user_registration.class_level is not None:
        if user_registration.class_level.years_until_graduation > 8:
            weights = [2, 1, 1, 1, 1, 0]
        elif user_registration.class_level.years_until_graduation == 8:
            weights = [1, 1, 1, 1, 2, 0]
    return series_general_weighted_sum(solutions, weights)


def series_Matik_sum(solutions, user_registration):
    weights = None
    if user_registration.class_level is not None:
        if user_registration.class_level.years_until_graduation > 5:
            weights = [2, 1, 1, 1, 1, 0]
        elif user_registration.class_level.years_until_graduation == 5:
            weights = [1, 1, 1, 1, 2, 0]
    return series_general_weighted_sum(solutions, weights)


def series_STROM_sum(solutions, user_registration):
    weights = None
    if user_registration.class_level is not None:
        if user_registration.class_level.years_until_graduation > 2:
            weights = [2, 1, 1, 1, 1, 0]
        elif user_registration.class_level.years_until_graduation == 2:
            weights = [1, 1, 1, 1, 2, 0]
    return series_general_weighted_sum(solutions, weights)


def series_STROM_4problems_sum(solutions, user_registration):
    weights = [1, 1, 1, 2]
    if user_registration.class_level is not None:
        if user_registration.class_level.years_until_graduation > 2:
            weights = [2, 1, 1, 1]
        elif user_registration.class_level.years_until_graduation == 2:
            weights = [1, 2, 1, 1]
        elif user_registration.class_level.years_until_graduation == 1:
            weights = [1, 1, 2, 1]
    return series_general_weighted_sum(solutions, weights)


def semester_simple_sum(series_subtotals):
    return sum(series_subtotals)


SERIES_SUM_METHODS = [
    ('series_simple_sum', 'Súčet bodov'),
    ('series_Malynar_sum', 'Súčet bodov + bonifikácia Malynár'),
    ('series_Matik_sum', 'Súčet bodov + bonifikácia Matik'),
    ('series_STROM_sum', 'Súčet bodov + bonifikácia STROM'),
    ('series_STROM_4problems_sum', 'Súčet bodov + bonifikácia STROM (ročníky XXXX-YYYY)')
]

SEMESTER_SUM_METHODS = [
    ('semester_simple_sum', 'Súčet bodov')
]
