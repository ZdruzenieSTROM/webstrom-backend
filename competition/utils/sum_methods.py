from competition.models import EventRegistration, Solution


def dot_product(solutions: list[int], weights: list[int]):
    return sum(s*w for s, w in zip(solutions, weights))


def solutions_to_list_of_points(solutions: list[Solution]) -> list[int]:
    return [s.score or 0 if s is not None else 0 for s in solutions]


def solutions_to_list_of_points_pretty(solutions: list[Solution]) -> list[str]:
    return [str(s.score or '?') if s is not None else '-' for s in solutions]


def series_simple_sum(solutions: list[int], user_registration=None):
    # pylint: disable=unused-argument
    # return sum([s.score or 0 for s in solutions if s is not None])
    return sum(solutions)


def series_general_weighted_sum(solutions: list[int], weights: list[int]):
    if weights:
        # points = solutions_to_list_of_points(solutions)
        points = solutions
        points.sort(reverse=True)
        return dot_product(points, weights)

    return series_simple_sum(solutions)


def series_Malynar_sum_until_2021(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = None
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 8:
            weights = [2, 1, 1, 1, 1, 0]
        elif user_registration.grade.years_until_graduation == 8:
            weights = [1, 1, 1, 1, 2, 0]
    return series_general_weighted_sum(solutions, weights)


def series_Malynar_sum(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = None
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 8:
            weights = [1, 2, 1, 1, 1, 0]
        elif user_registration.grade.years_until_graduation == 8:
            weights = [1, 1, 1, 2, 1, 0]
    return series_general_weighted_sum(solutions, weights)


def series_Matik_sum_until_2021(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = None
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 5:
            weights = [2, 1, 1, 1, 1, 0]
        elif user_registration.grade.years_until_graduation == 5:
            weights = [1, 1, 1, 1, 2, 0]
    return series_general_weighted_sum(solutions, weights)


def series_Matik_sum(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = None
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 5:
            weights = [1, 2, 1, 1, 1, 0]
        elif user_registration.grade.years_until_graduation == 5:
            weights = [1, 1, 1, 2, 1, 0]
    return series_general_weighted_sum(solutions, weights)


def series_STROM_sum_until_2021(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = None
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 2:
            weights = [2, 1, 1, 1, 1, 0]
        elif user_registration.grade.years_until_graduation == 2:
            weights = [1, 1, 1, 1, 2, 0]
    return series_general_weighted_sum(solutions, weights)


def series_STROM_sum(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = None
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 2:
            weights = [1, 2, 1, 1, 1, 0]
        elif user_registration.grade.years_until_graduation == 2:
            weights = [1, 1, 1, 2, 1, 0]
    return series_general_weighted_sum(solutions, weights)


def series_STROM_4problems_sum(solutions, user_registration: EventRegistration):
    # pylint: disable=invalid-name
    weights = [1, 1, 1, 2]
    if user_registration.grade is not None:
        if user_registration.grade.years_until_graduation > 2:
            weights = [2, 1, 1, 1]
        elif user_registration.grade.years_until_graduation == 2:
            weights = [1, 2, 1, 1]
        elif user_registration.grade.years_until_graduation == 1:
            weights = [1, 1, 2, 1]
    return series_general_weighted_sum(solutions, weights)
