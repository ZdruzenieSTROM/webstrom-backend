import sqlite3
from django.core.management import BaseCommand
from competition.models import Semester,Series,Problem
SERIES_QUERY = '''SELECT id,number,submission_deadline, sum_method,season_id
FROM competitions_series'''

SEMESTER_QUERY = ''' SELECT id,competition_id,end,name,year,number,start FROM competition_season'''

PROBLEM_QUERY = '''
SELECT text,series.id AS series_id,season.id AS season_id,season.name,submission_deadline,series.sum_method,season.competition_id,year
FROM competitions_season AS season
INNER JOIN competitions_series AS series ON series.season_id=season.id
INNER JOIN problems_problemset AS problemset ON series.problemset_id=problemset.id
INNER JOIN problems_probleminset AS inset ON inset.problemset_id=problemset.id
INNER JOIN problems_problem AS problem ON problem.id=inset.problem_id'''

COMPETITION_ID_MAPPING ={
    1:1,
    2:3,
    3:2
} 

SUM_METHOD_DICT={
    'SUCET_SERIE_35':'',
    'SUCET_SERIE_32':'',
    'SUCET_SERIE_MATIK':'',
    'SUCET_SERIE_MALYNAR':'',
}

class Command(BaseCommand):

    def _load_semester(self,conn,competition_id_mapping):
        semester_id_mapping={}
        conn.execute(SEMESTER_QUERY)
        semesters = conn.fetchall()
        for semester in semesters:
            new_semester = Semester(
                season_code=semester['number']-1,
                competition=['semester.competition_id'],
                year=semester['year'],
                school_year=to_school_year(semester['year']),
                start=semester['start'],
                end=semester['end']
            )
            new_semester.save()
            semester_id_mapping[semester['id']] = new_semester.id
        return semester_id_mapping

    def _load_series(self,conn,semester_id_mapping):
        series_id_mapping = {}
        conn.execute(SERIES_QUERY)
        series_all = conn.fetchall()
        for series in series_all:
            new_series = Series(
                semester=semester_id_mapping[series['season_id']],
                order=series['number'],
                deadline=series['submission_deadline'],
                complete=series['is_active']==0,
                sum_method=SUM_METHOD_DICT[series['sum_method']]

            )
            new_series.save()
            series_id_mapping[series['id']] = new_series.id
        return series_id_mapping

    def _load_problems(self,conn,series_id_mapping):
        problem_id_mapping = {}
        conn.execute(PROBLEM_QUERY)
        problems = conn.fetchall()
        for problem in problems:
            new_problem = Problem(
                text=problem['text'],
                series=series_id_mapping[problem['series_id']],
                order=problem['order']
            )
            new_problem.save()
            problem_id_mapping[problem['id']] = new_problem.id
        return problem_id_mapping

    def _load_competitions(self,conn):
        semester_id_mapping = self._load_semester(conn,COMPETITION_ID_MAPPING)
        series_id_mapping = self._load_series(conn,semester_id_mapping)
        problem_id_mapping = self._load_problems(conn,series_id_mapping)

    def _load_users(self,conn):
        pass

    def _load_results(self,conn):
        pass

    def handle(self, *args, **options):
        if len(args)>1:
            raise ValueError('DB not specified')
        try:
            conn = sqlite3.connect(args[0])
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
            pass
        finally:
            if conn:
                conn.close()