import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from io import BytesIO

from django.core.exceptions import ValidationError as CoreValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Count
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from competition import models
from competition.views import parse_corrected_solution_name_parts
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


PDF_CONTENT = (b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'
               b'trailer\n<< /Root 1 0 R >>\n%%EOF\n')


def make_zip(files: dict) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return stream.getvalue()


class TestParseCorrectedSolutionName(SimpleTestCase):
    '''parse_corrected_solution_name_parts'''

    def test_basic(self):
        self.assertEqual(
            parse_corrected_solution_name_parts('5-JanNovak-12-34.pdf'), (5, 12, 34))

    def test_ignores_folders(self):
        self.assertEqual(
            parse_corrected_solution_name_parts('opravene/Do24Hodin/5-JanNovak-12-34.pdf'),
            (5, 12, 34))
        self.assertEqual(
            parse_corrected_solution_name_parts('opravene\\5-JanNovak-12-34.pdf'), (5, 12, 34))

    def test_uppercase_extension(self):
        self.assertEqual(
            parse_corrected_solution_name_parts('5-JanNovak-12-34.PDF'), (5, 12, 34))

    def test_dash_in_name(self):
        self.assertEqual(
            parse_corrected_solution_name_parts('5-JanaNovák-Kováčová-12-34.pdf'), (5, 12, 34))

    def test_does_not_strip_characters_from_ids(self):
        with self.assertRaisesMessage(CoreValidationError, '34_corrected'):
            parse_corrected_solution_name_parts('5-JanNovak-12-34_corrected.pdf')

    def test_too_few_parts(self):
        with self.assertRaisesMessage(CoreValidationError, 'nie je v správnom formáte'):
            parse_corrected_solution_name_parts('5-12-34.pdf')
        with self.assertRaisesMessage(CoreValidationError, 'nie je v správnom formáte'):
            parse_corrected_solution_name_parts('JanNovak-34.pdf')

    def test_without_score(self):
        self.assertEqual(
            parse_corrected_solution_name_parts('JanNovak-12-34.pdf'), (None, 12, 34))
        self.assertEqual(
            parse_corrected_solution_name_parts('Do24Hodin/Jana-Kovacova-12-34.pdf'),
            (None, 12, 34))

    def test_score_out_of_range(self):
        with self.assertRaises(CoreValidationError):
            parse_corrected_solution_name_parts('12-JanNovak-12-34.pdf')


class TestUploadCorrectedSolutions(APITestCase, PermissionTestMixin):
    '''competition/problem/<pk>/upload-corrected'''
    # pylint: disable=too-many-public-methods

    fixtures = get_app_fixtures([
        'base',
        'user',
        'personal',
        'competition'
    ])

    def setUp(self):
        self.create_users()
        self.problem = (models.Problem.objects
                        .annotate(solution_count=Count('solution'))
                        .filter(solution_count__gte=2)
                        .order_by('pk')
                        .first())
        self.solutions = list(
            self.problem.solution_set.order_by('pk')[:2])
        for solution in self.solutions:
            solution.score = None
            solution.save()
        self.other_solution = (models.Solution.objects
                               .exclude(problem=self.problem)
                               .order_by('pk')
                               .first())

        self.storage_dir = tempfile.mkdtemp()
        storage = models.private_storage
        self.original_location = storage._location  # pylint: disable=protected-access
        storage._location = self.storage_dir  # pylint: disable=protected-access
        storage.__dict__.pop('base_location', None)
        storage.__dict__.pop('location', None)

    def tearDown(self):
        storage = models.private_storage
        storage._location = self.original_location  # pylint: disable=protected-access
        storage.__dict__.pop('base_location', None)
        storage.__dict__.pop('location', None)
        shutil.rmtree(self.storage_dir, ignore_errors=True)

    def url(self, problem=None):
        return f'/api/competition/problem/{(problem or self.problem).pk}/upload-corrected/'

    @staticmethod
    def name(solution, score=5):
        return f'{score}-JanNovak-{solution.problem_id}-{solution.semester_registration_id}.pdf'

    def upload(self, content: bytes, user='strom', filename='opravene.zip'):
        client = self.get_client(user)
        return client.post(
            self.url(),
            {'file': SimpleUploadedFile(filename, content)},
            format='multipart')

    def assert_nothing_saved(self):
        for solution in self.solutions:
            solution.refresh_from_db()
            self.assertIsNone(solution.score)
            self.assertFalse(solution.corrected_solution)

    def test_files_in_root(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0], 5): PDF_CONTENT,
            self.name(self.solutions[1], 7): PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(response.json()['uploaded']), 2)
        self.assertEqual(response.json()['skipped'], [])
        self.solutions[0].refresh_from_db()
        self.solutions[1].refresh_from_db()
        self.assertEqual(self.solutions[0].score, 5)
        self.assertEqual(self.solutions[1].score, 7)
        self.assertTrue(self.solutions[0].corrected_solution)

    def test_files_in_subfolders(self):
        response = self.upload(make_zip({
            'opravene/' + self.name(self.solutions[0], 3): PDF_CONTENT,
            'opravene/Do24Hodin/' + self.name(self.solutions[1], 4): PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        self.solutions[0].refresh_from_db()
        self.solutions[1].refresh_from_db()
        self.assertEqual(self.solutions[0].score, 3)
        self.assertEqual(self.solutions[1].score, 4)

    def test_uppercase_extension(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0]).replace('.pdf', '.PDF'): PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        self.solutions[0].refresh_from_db()
        self.assertEqual(self.solutions[0].score, 5)

    def test_non_pdf_is_skipped(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0]): PDF_CONTENT,
            'poznamky.txt': b'ahoj',
        }))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(response.json()['uploaded']), 1)
        self.assertEqual(response.json()['skipped'][0]['filename'], 'poznamky.txt')

    def test_metadata_ignored(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0]): PDF_CONTENT,
            '__MACOSX/._' + self.name(self.solutions[0]): b'metadata',
            '.DS_Store': b'metadata',
        }))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['skipped'], [])

    def assert_only_first_saved(self, score=5):
        self.solutions[0].refresh_from_db()
        self.solutions[1].refresh_from_db()
        self.assertEqual(self.solutions[0].score, score)
        self.assertTrue(self.solutions[0].corrected_solution)
        self.assertIsNone(self.solutions[1].score)
        self.assertFalse(self.solutions[1].corrected_solution)

    def test_mix_saves_valid_and_reports_invalid(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0]): PDF_CONTENT,
            f'5-JanNovak-{self.problem.pk}-abc.pdf': PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(len(data['uploaded']), 1)
        self.assertEqual(len(data['errors']), 1)
        self.assertIn('Posledná časť názvu (id registrácie)', data['errors'][0]['reason'])
        self.assert_only_first_saved()

    def test_only_invalid_files(self):
        response = self.upload(make_zip({
            f'5-JanNovak-{self.problem.pk}-abc.pdf': PDF_CONTENT,
            self.name(self.solutions[1]): b'toto nie je pdf',
        }))
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('Nič sa neuložilo. Počet súborov s chybou: 2.', data['detail'])
        self.assertEqual(len(data['errors']), 2)
        self.assert_nothing_saved()

    def test_without_score_uploads_pdf_and_warns(self):
        self.solutions[0].score = 4
        self.solutions[0].save()
        response = self.upload(make_zip({
            self.name(self.solutions[0]).split('-', 1)[1]: PDF_CONTENT,
            self.name(self.solutions[1], 6): PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(len(data['uploaded']), 2)
        self.assertEqual(len(data['warnings']), 1)
        self.assertIn('body ostali nezmenené', data['warnings'][0]['reason'])
        self.solutions[0].refresh_from_db()
        self.solutions[1].refresh_from_db()
        self.assertEqual(self.solutions[0].score, 4)
        self.assertTrue(self.solutions[0].corrected_solution)
        self.assertEqual(self.solutions[1].score, 6)

    def test_only_non_pdf_files(self):
        response = self.upload(make_zip({'poznamky.txt': b'ahoj', 'obrazok.png': b'png'}))
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('nenašlo žiadne opravené riešenie', data['detail'])
        self.assertEqual(len(data['skipped']), 2)

    def test_empty_zip(self):
        response = self.upload(make_zip({}))
        self.assertEqual(response.status_code, 400)
        self.assertIn('nenašlo žiadne opravené riešenie', response.json()['detail'])

    def test_nested_zip(self):
        inner = make_zip({self.name(self.solutions[0]): PDF_CONTENT})
        response = self.upload(make_zip({'vnutorny.zip': inner}))
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('ZIP v ZIPe', data['skipped'][0]['reason'])
        self.assert_nothing_saved()

    def test_file_for_other_problem(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0]): PDF_CONTENT,
            self.name(self.other_solution): PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('patrí k úlohe', response.json()['errors'][0]['reason'])
        self.assert_only_first_saved()
        self.other_solution.refresh_from_db()
        self.assertFalse(self.other_solution.corrected_solution)

    def test_duplicate_solution_saves_neither(self):
        response = self.upload(make_zip({
            self.name(self.solutions[1], 5): PDF_CONTENT,
            'iny/' + self.name(self.solutions[1], 6): PDF_CONTENT,
            self.name(self.solutions[0], 5): PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 200, response.content)
        errors = response.json()['errors']
        self.assertEqual(len(errors), 2)
        self.assertIn('Duplicitné riešenie', errors[0]['reason'])
        self.assert_only_first_saved()

    def test_fake_pdf(self):
        response = self.upload(make_zip({
            self.name(self.solutions[0]): PDF_CONTENT,
            self.name(self.solutions[1]): b'toto nie je pdf',
        }))
        self.assertEqual(response.status_code, 200, response.content)
        errors = response.json()['errors']
        self.assertEqual(len(errors), 1)
        self.assertIn('obsah nie je PDF', errors[0]['reason'])
        self.assert_only_first_saved()

    def test_unknown_registration(self):
        response = self.upload(make_zip({
            f'5-JanNovak-{self.problem.pk}-999999.pdf': PDF_CONTENT,
        }))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Registrácia používateľa s id 999999 neexistuje',
                      response.json()['errors'][0]['reason'])

    def test_not_a_zip(self):
        response = self.upload(b'toto nie je zip', filename='opravene.zip')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Priložený súbor nie je zip')

    def test_only_staff(self):
        content = make_zip({self.name(self.solutions[0]): PDF_CONTENT})
        self.assertEqual(self.upload(content, user='competitor').status_code, 403)
        self.assert_nothing_saved()
