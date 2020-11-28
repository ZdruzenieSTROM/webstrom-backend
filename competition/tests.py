from rest_framework.test import APITestCase
from tests.test_utils import get_app_fixtures

series_expected_keys = [
    'id',
    'problems',
    'order',
    'deadline',
    'complete',
    'frozen_results',
    'semester',
]

problem_expected_keys = [
    'id',
    'text',
    'order',
    'series',
]

results_row_expected_keys = [
    'rank_start',
    'rank_end',
    'rank_changed',
    'registration',
    'subtotal',
    'total',
    'solutions',
]

solution_expected_keys = [
    'points',
    'solution_pk',
    'problem_pk',
]

semester_expected_keys = [
    'id',
    'series_set',
    'year',
    'school_year',
    'start',
    'end',
    'season_code',
    'frozen_results',
    'competition',
    'late_tags',
]


def series_assert_format(self, series):
    '''assert given series format'''
    for key in series_expected_keys:
        self.assertIn(key, series)
    self.assertEqual(len(series['problems']), 6)
    for key in problem_expected_keys:
        self.assertIn(key, series['problems'][0])


def results_row_assert_format(self, results_row, solutions_expected_count):
    '''assert given results_row format'''
    for key in results_row_expected_keys:
        self.assertIn(key, results_row)
    self.assertEqual(len(results_row['solutions']), solutions_expected_count)
    self.assertEqual(len(results_row['solutions'][0]), 6)
    for key in solution_expected_keys:
        self.assertIn(key, results_row['solutions'][0][0])


def semester_assert_format(self, semester):
    '''assert given semester format'''
    for key in semester_expected_keys:
        self.assertIn(key, semester)
    self.assertEqual(len(semester['series_set']), 2)
    series_assert_format(self, semester['series_set'][0])


class TestSeries(APITestCase):
    '''competition/series'''

    URL_PREFIX = '/competition/series'

    fixtures = get_app_fixtures([
        'base',
        'competition',
        'personal',
        'user'
    ])

    def test_get_series_current(self):
        '''/current format ok'''
        response = self.client.get(self.URL_PREFIX + '/current', {}, 'json')
        self.assertEqual(response.status_code, 200)
        series_assert_format(self, response.json())

    def test_get_series_specific(self):
        '''/0 format ok'''
        response = self.client.get(self.URL_PREFIX + '/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        series_assert_format(self, response.json())

    def test_get_series_result_specific(self):
        '''/0/results format ok'''
        response = self.client.get(self.URL_PREFIX + '/0/results', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        results_row_assert_format(self, response.json()[0], 1)


class TestSemester(APITestCase):
    '''competition/semester'''

    URL_PREFIX = '/competition/semester'

    fixtures = get_app_fixtures([
        'base',
        'competition',
        'personal',
        'user'
    ])

    def test_get_semester_current(self):
        '''/current format ok'''
        response = self.client.get(self.URL_PREFIX + '/current', {}, 'json')
        self.assertEqual(response.status_code, 200)
        semester_assert_format(self, response.json())

    def test_get_semester_specific(self):
        '''/0 format ok'''
        response = self.client.get(self.URL_PREFIX + '/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        semester_assert_format(self, response.json())

    def test_get_semster_result_specific(self):
        '''/0/results format ok'''
        response = self.client.get(self.URL_PREFIX + '/0/results', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        results_row_assert_format(self, response.json()[0], 2)


class TestCompetition(APITestCase):
    '''competition/competition'''
    URL_PREFIX = '/competition/competition'

    fixtures = get_app_fixtures([
        'base',
        'competition',
        'personal',
        'user'
    ])

    competition_expected_keys = [
        'name',
        'start_year',
        'description',
        'rules',
        'competition_type',
        'min_years_until_graduation',
    ]

    def competition_assert_format(self, comp, num_events):
        '''assert given competition format'''
        for key in self.competition_expected_keys:
            self.assertIn(key, comp)
        self.assertEqual(len(comp['event_set']), num_events)

    def test_get_competition_list(self):
        '''/ format OK'''
        response = self.client.get(self.URL_PREFIX + '/', {}, 'json')
        self.assertEqual(response.status_code, 200)

    def test_post_competition_list(self):
        '''post not allowed OK'''
        response = self.client.post(self.URL_PREFIX + '/', {})
        self.assertEqual(response.status_code, 405)

    def test_get_competition_detail(self):
        '''/0 format OK'''
        response = self.client.get(self.URL_PREFIX + '/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.competition_assert_format(response.json(), 6)
