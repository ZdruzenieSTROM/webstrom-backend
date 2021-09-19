import datetime
import sqlite3
from django.core.management import BaseCommand
from competition.models import Semester,Series,Problem,Competition
from competition.utils import get_school_year_by_date
SERIES_QUERY = '''SELECT id,number,submission_deadline, sum_method,season_id
FROM competitions_series'''

SEMESTER_QUERY = ''' SELECT id,competition_id,end,name,year,number,start FROM competitions_season'''

PROBLEM_QUERY = '''
SELECT text,series.id AS series_id,season.id AS season_id,season.name,submission_deadline,series.sum_method,season.competition_id,year, inset.position AS position, problem.id AS id
FROM competitions_season AS season
INNER JOIN competitions_series AS series ON series.season_id=season.id
INNER JOIN problems_problemset AS problemset ON series.problemset_id=problemset.id
INNER JOIN problems_probleminset AS inset ON inset.problemset_id=problemset.id
INNER JOIN problems_problem AS problem ON problem.id=inset.problem_id'''

COMPETITION_ID_MAPPING ={
    1:Competition.objects.get(pk=1),
    2:Competition.objects.get(pk=3),
    3:Competition.objects.get(pk=2)
}

SUM_METHOD_DICT={
    'SUCET_SERIE_35':'',
    'SUCET_SERIE_32':'',
    'SUCET_SERIE_MATIK':'',
    'SUCET_SERIE_MALYNAR':'',
}

def to_school_year(year,competition):
    return get_school_year_by_date(datetime.date(day=1,month=10,year=competition.start_year + year))

class Command(BaseCommand):

    def _load_semester(self,conn,competition_id_mapping):
        semester_id_mapping={}
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
                start=semester['start'],
                end=semester['end']
            )
            new_semester.save()
            semester_id_mapping[semester['id']] = new_semester
        return semester_id_mapping

    def _load_series(self,conn,semester_id_mapping):
        series_id_mapping = {}
        cursor = conn.cursor()
        cursor.execute(SERIES_QUERY)
        series_all = cursor.fetchall()
        for series in series_all:
            new_series = Series(
                semester=semester_id_mapping[series['season_id']],
                order=series['number'],
                deadline=series['submission_deadline'],
                complete=False,
                sum_method=SUM_METHOD_DICT[series['sum_method']]

            )
            new_series.save()
            series_id_mapping[series['id']] = new_series
        return series_id_mapping

    def _load_problems(self,conn,series_id_mapping):
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

    def _load_competitions(self,conn):
        semester_id_mapping = self._load_semester(conn,COMPETITION_ID_MAPPING)
        series_id_mapping = self._load_series(conn,semester_id_mapping)
        problem_id_mapping = self._load_problems(conn,series_id_mapping)

    def _load_users(self,conn):
        pass

    def _load_results(self,conn):
        pass


    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('db', type=str)

    def handle(self, *args, **options):
        conn=None
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
        except:
            raise
        finally:
            if conn:
                conn.close()
