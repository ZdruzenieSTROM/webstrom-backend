from datetime import datetime, timezone

from rest_framework.test import APITestCase

from competition import models
from tests.test_utils import PermissionTestMixin, get_app_fixtures

series_expected_keys = [
    'id',
    'problems',
    'order',
    'deadline',
    'complete',
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


class TestSeries(APITestCase, PermissionTestMixin):
    '''competition/series'''

    URL_PREFIX = '/api/competition/series'

    fixtures = get_app_fixtures([
        'base',
        'user',
        'personal',
        'competition'
    ])

    def setUp(self):
        self.create_users()

    def test_get_series_current(self):
        '''/current/0 format ok'''
        self.get_client()
        response = self.client.get(self.URL_PREFIX + '/current/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        series_assert_format(self, response.json())

    def test_get_series_specific(self):
        '''/0 format ok'''
        self.get_client()
        response = self.client.get(self.URL_PREFIX + '/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        series_assert_format(self, response.json())

    def test_get_series_result_specific(self):
        '''/0/results format ok'''
        self.get_client()
        response = self.client.get(self.URL_PREFIX + '/0/results', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        results_row_assert_format(self, response.json()[0], 1)

    def test_permission_list(self):
        responses = {user_name: 200 for user_name in self.user_settings}
        responses[None] = 200
        self.check_permissions(self.URL_PREFIX+'/', 'GET', responses)

    def test_permission_retrieve(self):
        self.check_permissions(self.URL_PREFIX + '/',
                               'GET', self.PUBLIC_OK_RESPONSES, {})

    def test_permission_update(self):
        self.check_permissions(self.URL_PREFIX + '/0/',
                               'PATCH', self.ONLY_STROM_OK_RESPONSES,
                               {
                                   "semester": 1,
                                   "order": 1,
                                   "deadline": "2020-01-01T18:00:00Z"
                               })

    def test_permission_create(self):
        self.check_permissions(self.URL_PREFIX + '/',
                               'POST', self.ONLY_STROM_OK_RESPONSES,
                               {
                                   "semester": 1,
                                   "order": 1,
                                   "deadline": "2020-01-01T18:00:00Z"
                               })


class TestSemester(APITestCase, PermissionTestMixin):
    '''competition/semester'''

    URL_PREFIX = '/api/competition/semester'

    fixtures = get_app_fixtures([
        'base',
        'user',
        'personal',
        'competition'
    ])

    def setUp(self):
        self.create_users()

    def test_get_semester_current(self):
        '''/current/0 format ok'''
        response = self.client.get(self.URL_PREFIX + '/current/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        semester_assert_format(self, response.json())

    def test_get_semester_specific(self):
        '''/0 format ok'''
        self.get_client()
        response = self.client.get(self.URL_PREFIX + '/0', {}, 'json')
        self.assertEqual(response.status_code, 200)
        semester_assert_format(self, response.json())

    def test_get_semster_result_specific(self):
        '''/0/results format ok'''
        self.get_client()
        response = self.client.get(self.URL_PREFIX + '/0/results', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        results_row_assert_format(self, response.json()[0], 2)

    def test_update_permissions(self):
        ''' update permission OK '''
        self.check_permissions(self.URL_PREFIX + '/0/',
                               'PATCH', self.ONLY_STROM_OK_RESPONSES, {'year': 2})
        self.check_permissions(self.URL_PREFIX + '/10/',
                               'PATCH', self.ONLY_KRICKY_OK_RESPONSES, {'year': 2})

    def test_public_points_permission(self):
        self.check_permissions(self.URL_PREFIX + '/',
                               'GET', self.PUBLIC_OK_RESPONSES, {})
        self.check_permissions(self.URL_PREFIX + '/current/0',
                               'GET', self.PUBLIC_OK_RESPONSES, {})
        self.check_permissions(self.URL_PREFIX + '/0/results',
                               'GET', self.PUBLIC_OK_RESPONSES, {})

    def test_staff_only_points_permissions(self):
        self.check_permissions(self.URL_PREFIX + '/0/schools',
                               'GET', self.ONLY_STAFF_OK_RESPONSES, {})
        self.check_permissions(self.URL_PREFIX + '/0/offline-schools',
                               'GET', self.ONLY_STAFF_OK_RESPONSES, {})
        self.check_permissions(self.URL_PREFIX + '/0/invitations/30/20',
                               'GET', self.ONLY_STAFF_OK_RESPONSES, {})
        self.check_permissions(self.URL_PREFIX + '/0/school-invitations/30/20',
                               'GET', self.ONLY_STAFF_OK_RESPONSES, {})


class TestAPISemester(APITestCase, PermissionTestMixin):
    '''competition/semester - Create all'''

    URL_PREFIX = '/api/competition/semester/'
    fixtures = PermissionTestMixin.get_basic_fixtures()

    def setUp(self):
        competition = models.Competition.objects.get(pk=0)
        self.semester = models.Semester.objects.create(
            competition=competition,
            school_year='2020/2021',
            season_code=1,
            start=datetime(2015, 6, 15, 23, 30, 1, tzinfo=timezone.utc),
            end=datetime(2016, 6, 15, 23, 30, 1, tzinfo=timezone.utc),
            year=44)
        self.create_users()

    def test_create_semester(self):
        data = {
            "year": 42,
            "school_year": "2017/2018",
            "start": "2017-10-02T22:00:00Z",
            "end": "2017-11-19T22:00:00Z",
            "season_code": 0,
            "competition": 0,
            "late_tags": []
        }
        self.check_permissions(self.URL_PREFIX,
                               'POST',
                               self.ONLY_STROM_OK_RESPONSES, data)
        self.assertEqual(models.Semester.objects.count(), 2)


class TestCompetition(APITestCase, PermissionTestMixin):
    '''competition/competition'''
    URL_PREFIX = '/api/competition/competition'

    fixtures = PermissionTestMixin.get_basic_fixtures()

    competition_expected_keys = [
        'name',
        'start_year',
        'description',
        'rules',
        'competition_type',
        'upcoming_or_current_event',
        'history_events',
        'min_years_until_graduation',
    ]

    def setUp(self):
        self.create_users()
        models.Event.objects.create(
            competition=models.Competition.objects.get(pk=1),
            year=44,
            school_year="2019/2020",
            start="2020-01-01T20:00:00+02:00",
            end="2020-06-01T20:00:00+02:00"
        )

    def competition_assert_format(self, comp, num_events):
        '''assert given competition format'''
        self.get_client()
        for key in self.competition_expected_keys:
            self.assertIn(key, comp)
        self.assertEqual(len(comp['history_events']), num_events)

    def test_get_competition_list(self):
        '''/ format OK'''
        self.get_client()
        response = self.client.get(self.URL_PREFIX + '/', {}, 'json')
        self.assertEqual(response.status_code, 200)

    def test_get_competition_detail(self):
        '''detail format OK'''
        response = self.client.get(self.URL_PREFIX + '/slug/strom', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.competition_assert_format(response.json(), 0)

        response = self.client.get(self.URL_PREFIX + '/slug/matik', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.competition_assert_format(response.json(), 1)

    def test_permission_list(self):
        '''list permission OK'''
        self.check_permissions(self.URL_PREFIX + '/',
                               'GET', self.PUBLIC_OK_RESPONSES)

    def test_permission_get(self):
        '''retrieve permission OK'''
        self.check_permissions(self.URL_PREFIX + '/slug/strom/',
                               'GET', self.PUBLIC_OK_RESPONSES)

    def test_permission_update(self):
        ''' update permission OK'''
        self.check_permissions(self.URL_PREFIX + '/0/', 'PUT',
                               self.ONLY_STROM_OK_RESPONSES,
                               {
                                   "id": 0,
                                   "name": "STROM",
                                   "slug": "strom",
                                   "start_year": 1976,
                                   "description": "popis",
                                   "rules": "# Pravidlá",
                                   "min_years_until_graduation": 0,
                                   "sites": [
                                       0
                                   ]
                               })

    def test_permission_create(self):
        ''' create permission OK'''
        self.check_permissions(self.URL_PREFIX + '/',
                               'POST', self.ALL_FORBIDDEN,
                               {'name': 'Ilegalna sutaz', 'start_year': 2020})


class TestSolution(APITestCase, PermissionTestMixin):
    '''competition/solution'''
    URL_PREFIX = '/api/competition/solution'

    fixtures = get_app_fixtures([
        'base',
        'competition',
        'personal',
        'user'
    ])

    def setUp(self):
        self.create_users()

    def test_add_positive_vote(self):
        ''' add_positive_vote OK'''
        self.check_permissions(self.URL_PREFIX + '/0/add-positive-vote/',
                               'POST',
                               self.ONLY_STAFF_OK_RESPONSES, {})
        vote = models.Solution.objects.get(pk=0).vote
        self.assertEqual(vote, 1)

    def test_add_negative_vote(self):
        ''' add_negative_vote OK'''
        self.check_permissions(self.URL_PREFIX + '/0/add-negative-vote/',
                               'POST',
                               self.ONLY_STAFF_OK_RESPONSES, {})
        vote = models.Solution.objects.get(pk=0).vote
        self.assertEqual(vote, -1)

    def test_remove_vote(self):
        ''' remove_vote OK'''
        models.Solution.objects.get(pk=0).set_vote(1)
        self.check_permissions(self.URL_PREFIX + '/0/remove-vote/',
                               'POST',
                               self.ONLY_STAFF_OK_RESPONSES, {})
        vote = models.Solution.objects.get(pk=0).vote
        self.assertEqual(vote, 0)
