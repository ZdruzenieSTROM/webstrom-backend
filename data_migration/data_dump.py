import csv
import datetime
import sqlite3
import sys
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
    'SUCET_SERIE_35': '',
    'SUCET_SERIE_32': '',
    'SUCET_SERIE_MATIK': '',
    'SUCET_SERIE_MALYNAR': '',
    'SUCET_SERIE_46': '',
    'SUCET_SERIE_MALYNAR_31': '',
    'SUCET_SERIE_MATIK_35': ''
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
        'text': problem['text'],
        'series': problem['series_id'],
        'order': problem['position']
    }


def transform_series(series):
    return {
        'semester': series['season_id'],
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


def build_result_row(rank_start, rank_end, list):

    return {
        "rank_start": 1,
        "rank_end": 1,
        "rank_changed": true,
        "registration": {
            "school": {
                "code": 160971,
                "name": "Gymnázium M.R.Štefánika",
                "abbreviation": "GNamL4KE",
                "street": "Nám. L. Novomeského 4",
                "city": "Košice-Staré Mesto",
                "zip_code": "04224"
            },
            "grade": "S3",
            "profile": {
                "first_name": "Ucastnik",
                "last_name": "Priezvisko58"
            }
        },
        "subtotal": [
            30,
            6
        ],
        "total": 36,
        "solutions": [
            [
                {
                    "points": "-",
                    "solution_pk": null,
                    "problem_pk": 0,
                    "votes": 0
                },

            ],
            [

                {
                    "points": "?",
                    "solution_pk": 391,
                    "problem_pk": 11,
                    "votes": 0
                }
            ]
        ]
    },


def parse_results():
    response = requests.get(
        'https://seminar.strom.sk/sk/sutaze/semester/poradie/posledny/')
    soup = bs4.BeautifulSoup(response.text)
    body: bs4.BeautifulSoup = soup.find_all(
        'table', {'class': 'table table-condensed table-striped'})[-1].find('tbody')
    for row in body.find_all('tr'):
        values = row.find_all('td')
        print([v.get_text().strip() for v in values])


def parse_one_day_competition(url):
    pass


if __name__ == '__main__':
    conn = get_connection(sys.argv[1])
    parse_results()
    # load_resource(conn, SEMESTER_QUERY, transform_semester, 'semesters.csv')
    # load_resource(conn, SERIES_QUERY, transform_series, 'series.csv')
    # load_resource(conn, PROBLEM_QUERY, transform_problem, 'problems.csv')
