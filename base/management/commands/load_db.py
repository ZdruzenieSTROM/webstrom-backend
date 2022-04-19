import datetime
import unidecode
import re
import sqlite3
from django.core.management import BaseCommand
from django.utils.dateparse import parse_datetime
from django.db.models import Q, F
import pytz
from allauth.account.models import EmailAddress

from competition.models import (
    EventRegistration, Semester, Series,
    Problem, Competition, Grade, Solution
)
from competition.utils import get_school_year_by_date
from user.models import User
from personal.models import Profile, School


SERIES_QUERY = '''
    SELECT id,number,submission_deadline, sum_method,season_id
    FROM competitions_series
'''

SEMESTER_QUERY = '''
    SELECT id,competition_id,end,name,year,number,start
    FROM competitions_season
'''

PROBLEM_QUERY = '''
    SELECT text,series.id AS series_id,season.id AS season_id,season.name,submission_deadline,series.sum_method,season.competition_id,year, inset.position AS position, problem.id AS id
    FROM competitions_season AS season
    INNER JOIN competitions_series AS series ON series.season_id=season.id
    INNER JOIN problems_problemset AS problemset ON series.problemset_id=problemset.id
    INNER JOIN problems_probleminset AS inset ON inset.problemset_id=problemset.id
    INNER JOIN problems_problem AS problem ON problem.id=inset.problem_id
'''

COMPETITION_ID_MAPPING = {
    1: Competition.objects.get(pk=1),
    2: Competition.objects.get(pk=3),
    3: Competition.objects.get(pk=2)
}

SCHOOL_QUERY = '''
    SELECT school.id,school.name AS school_name,addr.street AS school_street,
            addr.city AS school_city,addr.postal_number AS school_zip_code
    FROM schools_school AS school
    INNER JOIN schools_address AS addr ON school.address_id=addr.id
'''

USERS_QUERY = '''
    SELECT user.id,user.email,user.is_staff,user.is_active,user.first_name,user.last_name, user.date_joined,
            user.username,user.is_superuser,user.password,phone_number,parent_phone_number,
            classlevel,prof.school_id AS school_id
    FROM auth_user AS user
    INNER JOIN profiles_userprofile AS prof ON prof.user_id=user.id
    WHERE last_name<>'' OR user.id IN (SELECT user_id FROM profiles_userseasonregistration)
'''

SOLUTION_QUERY = '''
    SELECT id,score,problem_id,user_id,added_at
    FROM problems_usersolution
'''
SEMESTERREG_QUERY = '''
    SELECT id,user_id,season_id,classlevel,school_id
    FROM profiles_userseasonregistration
'''

SUM_METHOD_DICT = {
    'SUCET_SERIE_35': '',
    'SUCET_SERIE_32': '',
    'SUCET_SERIE_MATIK': '',
    'SUCET_SERIE_MALYNAR': '',
    'SUCET_SERIE_46': '',
    'SUCET_SERIE_MALYNAR_31': '',
    'SUCET_SERIE_MATIK_35': ''
}


def localize(date):
    return pytz.timezone("Europe/Helsinki").localize(
        parse_datetime(date),
        is_dst=None
    )


def to_school_year(year, competition):
    return get_school_year_by_date(
        datetime.date(day=1, month=10, year=competition.start_year + year)
    )


def get_type(name):
    clean_name = unidecode.unidecode(name.lower())
    if 'gymnazium' in clean_name:
        return 0
    elif 'stredna' in clean_name or 'ss' in clean_name:
        return 1
    elif 'zakladna' in clean_name or 'zs' in clean_name:
        return 2
    elif 'spojena skola' in clean_name:
        return 3


def estimate_school(school_dict):
    type = get_type(school_dict['school_name'])
    city_regex = r'^'+re.escape(school_dict['school_city'])+r'(-.*)?$'
    schools_in_city = School.objects.filter(
        Q(zip_code=school_dict['school_zip_code'].replace(' ', '')) |
        Q(city__regex=city_regex)
    )
    schools = schools_in_city.filter(
        name__iexact=school_dict['school_name'].lower())
    if schools.count() == 1:
        return schools.first()

    # Filter by type
    schools = [school for school in schools_in_city if get_type(
        school.name) == type]
    if len(schools) == 1:
        return schools[0]

    # Filter by address
    def match_address(addr1, addr2):
        def parse(addr):
            street = ''.join(filter(lambda ch: ch.isalpha(), addr))
            street = unidecode.unidecode(street.lower()).replace(' ', '')
            number = re.search(r'(\d+/)?(\d+)', addr)
            if number is not None:
                number = number.group(2)
            return street, number
        street1, number1 = parse(addr1)
        street2, number2 = parse(addr2)
        if street1 == street2:
            if number1 is None or number2 is None or number1 == number2:
                return True
        return False

    schools = [school for school in schools
               if match_address(school.street, school_dict['school_street'])]
    if len(schools) == 1:
        return schools[0]
    print(schools)
    #     x = input()
    raise School.DoesNotExist


class Command(BaseCommand):

    def _load_semester(self, conn, competition_id_mapping):
        semester_id_mapping = {}
        cursor = conn.cursor()
        cursor.execute(SEMESTER_QUERY)
        semesters = cursor.fetchall()
        for semester in semesters:
            new_semester = Semester(
                season_code=semester['number']-1,
                competition=competition_id_mapping[semester['competition_id']],
                year=semester['year'],
                school_year=to_school_year(
                    semester['year'],
                    competition_id_mapping[semester['competition_id']]),
                start=localize(semester['start']),
                end=localize(semester['end'])
            )
            new_semester.save()
            semester_id_mapping[semester['id']] = new_semester
        return semester_id_mapping

    def _load_series(self, conn, semester_id_mapping):
        series_id_mapping = {}
        cursor = conn.cursor()
        cursor.execute(SERIES_QUERY)
        series_all = cursor.fetchall()
        for series in series_all:
            new_series = Series(
                semester=semester_id_mapping[series['season_id']],
                order=series['number'],
                deadline=localize(series['submission_deadline']),
                complete=False,
                sum_method=SUM_METHOD_DICT[series['sum_method']]

            )
            new_series.save()
            series_id_mapping[series['id']] = new_series
        return series_id_mapping

    def _load_problems(self, conn, series_id_mapping):
        problem_id_mapping = {}
        cursor = conn.cursor()
        cursor.execute(PROBLEM_QUERY)
        problems = cursor.fetchall()
        for problem in problems:
            new_problem = Problem(
                text=problem['text'],
                series=series_id_mapping[problem['series_id']],
                order=problem['position']
            )
            new_problem.save()
            problem_id_mapping[problem['id']] = new_problem
        return problem_id_mapping

    def _load_competitions(self, conn):
        semester_id_mapping = self._load_semester(conn, COMPETITION_ID_MAPPING)
        series_id_mapping = self._load_series(conn, semester_id_mapping)
        problem_id_mapping = self._load_problems(conn, series_id_mapping)
        return semester_id_mapping, series_id_mapping, problem_id_mapping

    def _load_users(self, conn, school_id_map):
        user_id_mapping = {}
        cursor = conn.cursor()
        cursor.execute(USERS_QUERY)
        users = cursor.fetchall()
        for user in users:
            new_user = None
            if user['email'] != '':
                new_user = User.objects.create_user(
                    email=user['email'],
                    verified_email=True,
                    is_staff=user['is_staff'],
                    is_active=user['is_active'],
                    date_joined=localize(user['date_joined']),

                )

                EmailAddress.objects.create(
                    user=new_user,
                    email=user['email'],
                    verified=True,
                    primary=True
                )
                new_user.password = user['password']
                # new_user.set_password(user['password'])
                new_user.save()
            try:
                grade = Grade.objects.get(
                    tag=user['classlevel']).get_year_of_graduation_by_date()
            except Grade.DoesNotExist:
                grade = 2000

            profile = Profile.objects.create(
                first_name=user['first_name'],
                last_name=user['last_name'],
                user=new_user,
                nickname=user['username'],
                school=school_id_map.get(
                    user['school_id'], School.objects.get_unspecified_value()),
                year_of_graduation=grade,
                phone=user['phone_number'] or '',
                parent_phone=user['parent_phone_number'] or '',
                gdpr=True
            )
            user_id_mapping[user['id']] = profile
        return user_id_mapping

    def _create_school_mapping(self, conn):
        school_id_mapping = {None: School.objects.get_unspecified_value()}
        cursor = conn.cursor()
        cursor.execute(SCHOOL_QUERY)
        schools = cursor.fetchall()
        success_counter = 0
        for school in schools:
            try:
                school_id = estimate_school(school)
                school_id_mapping[school['id']] = school_id
                success_counter += 1
            except School.DoesNotExist:
                print(f'Nepodarilo sa matchnút {school}')
                school_id_mapping[school['id']
                                  ] = School.objects.get_unspecified_value()
        print(
            f'Úspešne pripárovaných {success_counter}/{len(school_id_mapping)}')
        return school_id_mapping

    def _load_user_registrations(self, conn, user_id_map, season_id_map, school_id_map):
        cursor = conn.cursor()
        cursor.execute(SEMESTERREG_QUERY)
        user_registrations = cursor.fetchall()
        for user_registration in user_registrations:
            try:
                grade = Grade.objects.get(tag=user_registration['classlevel'])
            except Grade.DoesNotExist:
                grade = Grade.objects.get(tag='XX')
            EventRegistration.objects.create(
                profile=user_id_map[user_registration['user_id']],
                school=school_id_map[user_registration['school_id']],
                grade=grade,
                event=season_id_map[user_registration['season_id']]
            )

    def _load_solutions(self, conn, problem_id_map, user_id_map):
        cursor = conn.cursor()
        cursor.execute(SOLUTION_QUERY)
        solutions = cursor.fetchall()
        for solution in solutions:
            try:
                Solution.objects.create(
                    problem=problem_id_map[solution['problem_id']],
                    semester_registration=EventRegistration.objects.get(
                        event=problem_id_map[solution['problem_id']
                                             ].series.semester,
                        profile=user_id_map[solution['user_id']]),
                    score=solution['score'],
                    uploaded_at=solution['added_at']
                )
            except EventRegistration.DoesNotExist:
                print(problem_id_map[solution['problem_id']
                                     ].series.semester)
                print(user_id_map[solution['user_id']])
                print('-'*30)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('db', type=str)

    def handle(self, *args, **options):
        conn = None
        try:
            conn = sqlite3.connect(options['db'])

            def dict_factory(cursor, row):
                row_dict = {}
                for idx, col in enumerate(cursor.description):
                    row_dict[col[0]] = row[idx]
                return row_dict
            conn.row_factory = dict_factory
            # semester_id_map, _, problem_id_map = self._load_competitions(
            #     conn)
            school_id_map = self._create_school_mapping(conn)
            # user_id_map = self._load_users(conn, school_id_map)
            # print(f'Načítaných {len(user_id_map)} používateľov')
            # self._load_user_registrations(
            #     conn, user_id_map, semester_id_map, school_id_map)
            # print(f'Načítané registrácie')
            # self._load_solutions(conn, problem_id_map, user_id_map)
        finally:
            if conn:
                conn.close()
