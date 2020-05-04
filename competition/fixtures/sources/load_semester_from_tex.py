#!/bin/env python3

import datetime
import json
import re

# from ..competition.models import Problem, UserSolution


class SemesterManager:
    def __init__(self, free_semester_id=0, free_seriesid=0, free_problem_id=0):
        self._semester_id = free_semester_id
        self._seriesid = free_seriesid
        self._problem_id = free_problem_id
        self._competition_id = 0

    def get_series_id(self):
        self._seriesid += 1
        return self._seriesid-1

    def get_problem_id(self):
        self._problem_id += 1
        return self._problem_id-1

    def get_competition_id(self):
        self._competition_id += 1
        return self._competition_id-1

    def get_semester_id(self):
        self._semester_id += 1
        return self._semester_id-1

    @staticmethod
    def django_repr(model_name, pk, fields):
        return {
            "model": model_name,
            "pk": pk,
            "fields": fields
        }

    def create_semester(self, comp_id, year, start, end, late_tags, season):
        fields = {
            "competition": comp_id,
            "year": year,
            "start": start,
            "end": end,
            "season": season
        }
        return SemesterManager.django_repr('competition.Semester', self.get_semester_id(), fields)

    def create_series(self, semester_id, order, deadline):
        fields = {
            "semester": semester_id,
            "order": order,
            "deadline": deadline,
            "complete": False,

        }
        return SemesterManager.django_repr('competition.series', self.get_series_id(), fields)

    def create_problem(self, text, series, order):
        fields = {
            'text': text,
            'series': series,
            'order': order,
        }
        return SemesterManager.django_repr('competition.Problem', self.get_problem_id(), fields)

    def create_new_semester_json(self, problems, competition_id, semester_year, semester_season, deadline1, deadline2):
        objects = []
        json_datetime_format = '%Y-%m-%dT%H:%M:%S+02:00'
        if deadline1:
            first_term = deadline1.strftime(json_datetime_format)
            start_sem = deadline1 - datetime.timedelta(days=20)
            start_sem = start_sem.strftime(json_datetime_format)
            if deadline2:
                end_sem = deadline2
            else:
                end_sem = deadline1 + datetime.timedelta(days=30)
            end_sem = end_sem.strftime(json_datetime_format)
        else:
            start_sem = '2020-01-01T20:00:00+02:00'
            first_term = '2020-03-01T20:00:00+02:00'
            end_sem = '2020-06-01T20:00:00+02:00'
        semester = self.create_semester(
            competition_id, semester_year, start_sem, end_sem, None, semester_season)
        objects.append(semester)
        semester_id = semester['pk']
        s1 = self.create_series(semester_id, 1, first_term)
        s1_key = s1['pk']
        objects.append(s1)
        s2 = self.create_series(semester_id, 2, end_sem)
        s2_key = s2['pk']
        objects.append(s2)
        for problem_series, problem_order, problem_text in problems:
            series_key = s1_key if problem_series == 1 else s2_key
            objects.append(self.create_problem(
                problem_text, series_key, problem_order))
        return objects


roman_numerals = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5,
    'VI': 6,


}


class SemesterLaTeXLoader():
    @staticmethod
    def itemizetohtml(text):
        text = re.sub(r'\\begin\{itemize\}','<ul>',text,flags=re.S)
        text = re.sub(r'\\end\{itemize\}','</ul>',text,flags=re.S)
        text = re.sub(r'\\begin\{enumerate\}','<ol>',text,flags=re.S)
        text = re.sub(r'\\end\{enumerate\}','</ol>',text,flags=re.S)
        text = re.sub(r'\\item(.*?)(?=\\item|$|\\end)',r'<li>\1</li>',text,flags=re.M |re.S)
        return text

    @staticmethod
    def replace_pair_tags(text,latex_start,latex_end,html_start_tag,html_end_tag):
        pass

    @staticmethod
    def latex2html(text):
        text =  SemesterLaTeXLoader.itemizetohtml(text)
        text.replace('~','&nbsp')
        text.replace('\\\\','<br>')
        return text

    @staticmethod
    def semester_latex2html(semester):
        return [ (s,u,SemesterLaTeXLoader.latex2html(problem)) for s,u,problem in semester]


    @staticmethod
    def remove_latex_comments(text):
        text = re.sub(
            r'\\begin\{comment\}.*?\\end\{comment\}', '', text, flags=re.S)
        return re.sub(r'^%.*$', r'', text, flags=re.M)

    @staticmethod
    def remove_authors(text):
        text = re.sub(r'\\textbf\{Autori .*?\}.*$', '', text, flags=re.S)
        return text

    @staticmethod
    def load_kricky(file_name, json_file=None):
        with open(file_name, 'r', encoding='utf8') as input_tex:
            text = input_tex.read()
            text = SemesterLaTeXLoader.remove_latex_comments(text)
            problems = re.findall(
                r'\\newcommand\{\\zad([^\{\}]+)s([^\{\}]+)\}\{(.*?)\}[^\{\}]*(?=\\newcommand|$)', text, flags=re.S)
            return [(roman_numerals[problem_series], roman_numerals[problem_order], problem_text.strip('\n')) for problem_order, problem_series, problem_text in problems]

    @staticmethod
    def load_strom(file_name):
        with open(file_name, 'r', encoding='utf8') as input_tex:
            text = input_tex.read()
            text = SemesterLaTeXLoader.remove_latex_comments(text)
            problems = re.findall(
                r'(\\ifcase\\numexpr\\value\{uloha\}-1|\\or).*?\{(.*?)\}[^\{\}]*?(?=\\fi|$|\\or)', text, flags=re.S)
            semester = []
            for i, problem in enumerate(problems):
                semester.append(((i//6)+1, (i % 6)+1, problem[1].strip('\n')))
            return semester

    @staticmethod
    def load_strom_old(file_name):
        with open(file_name, 'r', encoding='utf8') as input_tex:
            text = input_tex.read()
            text = SemesterLaTeXLoader.remove_latex_comments(text)
            text = SemesterLaTeXLoader.remove_authors(text)
            problems = re.findall(
                r'\\uloha\{([^\{\}]+)\.\}\{(.*?)\}[^\{\}]*?(?=\\uloha|\\znak|$)', text, flags=re.S)
            semester = []
            for i, problem in enumerate(problems):
                semester.append(((i//6)+1, (i % 6)+1, problem[1].strip('\n')))
            try:
                (_, d1), (_, d2) = re.findall(
                    r'\\znak\{(.)\}\{.*?\}\{(.*?)\}', text, flags=re.S)
                d1, d2 = d1.replace('~', ''), d2.replace('~', '')
                d1 = datetime.datetime.strptime(d1, '%d.%m.%Y')
                d2 = datetime.datetime.strptime(d2, '%d.%m.%Y')
            except:
                d1, d2 = None, None
            print(d1, d2)
            return semester, d1, d2


comp_ids = {
    'STROM': 0,
    'Matik': 1,
    'Malynar': 2,
}


def process_files(files):
    objects = []
    manager = SemesterManager()
    for file in files:
        match = re.findall(r'(.+?)-(.+?)-(.+?).tex', file)
        if len(match) == 1:
            seminar, year, season = match[0]
            year = int(year)
        else:
            print(
                f'Skipping \"{file}\": File name is not in format Seminar-year-season.tex ')
            continue

        if season == '2':
            season = 'Letný'
        else:
            season = 'Zimný'
        d1, d2 = None, None
        if seminar == 'STROM':
            if year > 44 or (year == 44 and season == 'Letný'):
                print(f'Parsing \"{file}\" with STROM-NEW template...')
                parsed = SemesterLaTeXLoader.load_strom(file)
            else:
                print(f'Parsing \"{file}\" with STROM-OLD template...')
                parsed, d1, d2 = SemesterLaTeXLoader.load_strom_old(file)
        else:
            print(f'Parsing \"{file}\" with Kricky template...')
            parsed = SemesterLaTeXLoader.load_kricky(file)
        parsed = SemesterLaTeXLoader.semester_latex2html(parsed)
        objects += manager.create_new_semester_json(
            parsed,
            competition_id=comp_ids[seminar],
            semester_year=year,
            semester_season=season,
            deadline1=d1,
            deadline2=d2
        )

    with open('semesters.json', 'w') as f:
        json.dump(objects, f, indent=4)


if __name__ == '__main__':
    files = ['STROM-44-2.tex', 'STROM-44-1.tex', 'STROM-43-2.tex',
             'STROM-43-1.tex', 'STROM-42-2.tex', 'STROM-42-1.tex']
    process_files(files)
