import datetime
import sqlite3

import pytz
from allauth.account.models import EmailAddress
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.dateparse import parse_datetime

from competition.models import Competition, Grade, Problem, Semester, Series
from competition.utils import get_school_year_by_date
from personal.models import Profile, School
from user.models import User

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

USERS_QUERY = '''
    SELECT user.email,user.is_staff,user.is_active,user.first_name,user.last_name, user.date_joined,
            user.username,user.is_superuser,user.password,phone_number,parent_phone_number,
            classlevel,school.name AS school_name,addr.street AS school_street,
            addr.city AS school_city,addr.postal_number AS school_zip_code
    FROM auth_user AS user
    INNER JOIN profiles_userprofile AS prof ON prof.user_id=user.id
    INNER JOIN schools_school AS school ON prof.school_id=school.id
    INNER JOIN schools_address AS addr ON school.address_id=addr.id
    WHERE email<>''
'''

SUM_METHOD_DICT = {
    'SUCET_SERIE_35': '',
    'SUCET_SERIE_32': '',
    'SUCET_SERIE_MATIK': '',
    'SUCET_SERIE_MALYNAR': '',
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


def estimate_school(user):
    school = School.objects.filter(name=user['school_name'])
    if school.count() == 1:
        return school.first()
    school = School.objects.filter(
        Q(street=user['school_street']),
        Q(zip_code=user['school_zip_code'].replace(
            ' ', '')) | Q(city=user['school_city'])
    )
    if school.count() == 1:
        return school.first()
    return School.objects.get_unspecified_value()


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

    def _load_users(self, conn):
        cursor = conn.cursor()
        cursor.execute(USERS_QUERY)
        users = cursor.fetchall()
        for user in users:
            new_user = User.objects.create_user(
                email=user['email'],
                verified_email=True,
                is_staff=user['is_staff'],
                is_active=user['is_active'],
                date_joined=localize(user['date_joined']),

            )
            email_address = EmailAddress(
                user=new_user,
                email=user['email'],
                verified=True,
                primary=True
            )
            email_address.save()
            new_user.password = user['password']
            # new_user.set_password(user['password'])
            new_user.save()
            school = estimate_school(user)
            try:
                grade = Grade.objects.get(
                    tag=user['classlevel']).get_year_of_graduation_by_date()
            except Grade.DoesNotExist:
                grade = 2000

            profile = Profile(
                first_name=user['first_name'],
                last_name=user['last_name'],
                user=new_user,
                nickname=user['username'],
                school=school,
                year_of_graduation=grade,
                phone=user['phone_number'],
                parent_phone=user['parent_phone_number'],
                gdpr=True
            )
            profile.save()

    def _load_results(self, conn):
        pass

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
            self._load_competitions(conn)
            self._load_users(conn)
            self._load_results(conn)
        finally:
            if conn:
                conn.close()
