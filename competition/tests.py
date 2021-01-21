from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from tests.test_utils import get_app_fixtures
from competition.models import Competition, Semester

from django.test import RequestFactory, TestCase
from datetime import datetime
from django.utils import timezone

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

class TestAPISemester(APITestCase):

    URL_PREFIX = '/competition/semester/'

    def setUp(self):
        competition = Competition.objects.create(
            name = 'Malynár',
            start_year = 1980,
            description = 'Pre deti',
            competition_type = 2)
        self.semester = Semester.objects.create(
            competition = competition,
            school_year = '2020/2021', 
            season_code = 1, 
            start = datetime(2015, 6, 15, 23, 30, 1, tzinfo=timezone.utc),
            end = datetime(2016, 6, 15, 23, 30, 1, tzinfo=timezone.utc),
            year = 44)

    def test_create_semester(self):
        data = {
            "id": 5,
            "series_set": [
                {
                    "id": 5,
                    "problems": [
                        {
                            "id": 71,
                            "text": "$ABCD$ je rovnobežník s ostrým uhlom $DAB$. Body $A,\\ P,\\ B,\\ D$ ležia na jednej kružnici v tomto poradí. Priamky $AP$ a $CD$ sa pretínajú v bode $Q$. Bod $O$ je stred kružnice opísanej trojuholníku $CPQ$. Dokážte, že ak $D \\neq O$, tak priamky $AD$ a $DO$ sú na seba kolmé.",
                            "order": 6,
                            "series": 11
                        }
                    ],
                    "order": 2,
                    "deadline": "2017-11-19T22:00:00Z",
                    "semester": 5
                }
            ],
            "semesterpublication_set": [],
            "unspecifiedpublication_set": [],
            "year": 42,
            "school_year": "2017/2018",
            "start": "2017-10-02T22:00:00Z",
            "end": "2017-11-19T22:00:00Z",
            "season_code": 0,
            "competition": 0,
            "late_tags": []
        }
        response = self.client.post(self.URL_PREFIX, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Semester.objects.count(), 1)
        self.assertEqual(Semester.objects.get().season_code, 1)


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
