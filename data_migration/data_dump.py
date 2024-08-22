import csv
import datetime
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from os import path
from typing import Optional

import bs4
import pytz
import requests
import unidecode
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

# from competition.utils.school_year_manipulation import get_school_year_by_date


def get_school_year_start_by_date(date: Optional[datetime.datetime] = None) -> int:
    if date is None:
        date = now()

    return date.year if date.month >= 9 else date.year - 1


def get_school_year_end_by_date(date: Optional[datetime.datetime] = None) -> int:
    return get_school_year_start_by_date(date) + 1


def get_school_year_by_date(date: Optional[datetime.datetime] = None) -> str:
    return f'{get_school_year_start_by_date(date)}/{get_school_year_end_by_date(date)}'


SEMESTER_QUERY = '''
    SELECT id,competition_id,end,name,year,number,start
    FROM competitions_season
'''
SERIES_QUERY = '''
    SELECT id,number,submission_deadline, sum_method,season_id
    FROM competitions_series
'''

PROBLEM_QUERY = '''
    SELECT text,series.id AS series_id,season.id AS season_id,season.name,submission_deadline,series.sum_method,season.competition_id,year, inset.position AS position, problem.id AS id
    FROM competitions_season AS season
    INNER JOIN competitions_series AS series ON series.season_id=season.id
    INNER JOIN problems_problemset AS problemset ON series.problemset_id=problemset.id
    INNER JOIN problems_probleminset AS inset ON inset.problemset_id=problemset.id
    INNER JOIN problems_problem AS problem ON problem.id=inset.problem_id
'''


SUM_METHOD_DICT = {
    'SUCET_SERIE_35': 'series_STROM_sum_until_2021',
    'SUCET_SERIE_32': 'series_STROM_4problems_sum',
    'SUCET_SERIE_MATIK': 'series_Matik_sum',
    'SUCET_SERIE_MALYNAR': 'series_Malynar_sum',
    'SUCET_SERIE_46': 'series_STROM_sum',
    'SUCET_SERIE_MALYNAR_31': 'series_Malynar_sum_until_2021',
    'SUCET_SERIE_MATIK_35': 'series_Matik_sum_until_2021'
}

COMPETITION_ID_MAPPING = {
    1: 0,
    2: 2,
    3: 1
}

START_YEAR = {
    0: 1976,
    1: 1987,
    2: 1991
}


def get_connection(db_path):
    conn = sqlite3.connect(db_path)

    def dict_factory(cursor, row):
        row_dict = {}
        for idx, col in enumerate(cursor.description):
            row_dict[col[0]] = row[idx]
        return row_dict
    conn.row_factory = dict_factory
    return conn


def localize(date):
    return pytz.timezone("Europe/Bratislava").localize(
        parse_datetime(date),
        is_dst=None
    )


def to_school_year(year, competition):
    return get_school_year_by_date(
        datetime.date(day=1, month=10, year=START_YEAR[competition] + year)
    )


def transform_semester(semester):
    return {
        'id': semester['id'],
        'season_code': semester['number']-1,
        'competition': COMPETITION_ID_MAPPING[semester['competition_id']],
        'year': semester['year'],
        'school_year': to_school_year(
            semester['year'],
            COMPETITION_ID_MAPPING[semester['competition_id']]),
        'start': localize(semester['start']),
        'end': localize(semester['end'])
    }


def transform_problem(problem):
    return {
        'id': problem['id'],
        'text': re.sub(r'\s+<li>', '<li>', problem['text']),
        'series_id': problem['series_id'],
        'order': problem['position']+1
    }


def transform_series(series):
    return {
        'id': series['id'],
        'semester_id': series['season_id'],
        'order': series['number'],
        'deadline': localize(series['submission_deadline']),
        'sum_method': SUM_METHOD_DICT[series['sum_method']]
    }


def load_resource(connection, query, tranform_func, output_filename):
    cursor = connection.cursor()
    cursor.execute(query)
    objects = cursor.fetchall()
    objects = list(map(tranform_func, objects))

    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(objects[0].keys()))
        writer.writeheader()
        writer.writerows(objects)


@dataclass
class SeriesResult:
    start: int
    end: int
    changed: bool
    school: str
    grade: str
    first_name: str
    last_name: str
    points: list[int]
    total: int

    def build_result_row(self):

        return {
            "rank_start": self.start,
            "rank_end": self.end,
            "rank_changed": self.changed,
            "registration": {
                "school": {
                    "code": "",
                    "name": self.school,
                    "abbreviation": "",
                    "street": "",
                    "city": "",
                    "zip_code": ""
                },
                "grade": self.grade,
                "profile": {
                    "first_name": self.first_name,
                    "last_name": self.last_name
                }
            },
            "subtotal": [
                sum(int(point) for point in series_points if point.isdigit()) for series_points in self.points

            ],
            "total": self.total,
            "solutions": [

                [
                    {
                        "points": point.replace('--', '-'),
                        "solution_pk": None,
                        "problem_pk": 0,
                        "votes": 0
                    } for point in series_points

                ] for series_points in self.points

            ]
        }


def parse_semester(rows: list):
    result_rows = []
    current_rank = None
    for values in rows:
        position = values[0]
        if position:
            current_rank = position
        num_problems = (len(values)-5)//2
        result_rows.append(SeriesResult(
            start=current_rank.split(' - ')[-1].strip('.'),
            end=current_rank.split('-')[0].strip('.'),
            changed=bool(position),
            first_name=' '.join(values[1].split(' ')[:-1]),
            last_name=values[1].split(' ')[0],
            grade=values[2],
            school=values[3],
            points=[values[4:4+num_problems],
                    values[4+num_problems:4+2*num_problems]],
            total=values[4+2*num_problems]
        )
        )
    return result_rows


def get_results_response(semester_id):
    for domain in ['matik', 'malynar', 'seminar']:
        response = requests.get(
            f'https://{domain}.strom.sk/sk/sutaze/semester/poradie/{semester_id}', timeout=5)
        if response.status_code == 200:
            return response
    raise ValueError(f'Invalid semester id: {semester_id}')


def parse_semester_results(semester_id):
    response = get_results_response(semester_id)
    soup = bs4.BeautifulSoup(response.text)
    body: bs4.BeautifulSoup = soup.find_all(
        'table', {'class': 'table table-condensed table-striped'})[-1].find('tbody')
    values = [[value.get_text().strip() for value in row.find_all('td')]
              for row in body.find_all('tr')]
    results = parse_semester(values)
    for series_values in series:
        results = parse_series(series_values)
    return {
        'event_ptr_id': semester_id,
        'frozen_resuts': json.dumps([row.build_result_row() for row in results])
    }


def parse_results():
    objects = []
    for i in range(74):
        try:
            objects.append(parse_semester_results(i))
        except ValueError as exc:
            print(exc)
    with open('semester_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(objects[0].keys()))
        writer.writeheader()
        writer.writerows(objects)


def parse_one_day_competition(url):
    pass


if __name__ == '__main__':
    conn = get_connection(sys.argv[1])
    parse_results()
    # load_resource(conn, SEMESTER_QUERY, transform_semester, 'semesters.csv')
    # load_resource(conn, SERIES_QUERY, transform_series, 'series.csv')
    # load_resource(conn, PROBLEM_QUERY, transform_problem, 'problems.csv')
