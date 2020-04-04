import re

#rom competition.models import Problem, UserSolution

roman_numerals={
    'I':1,
    'II':2,
    'III':3,
    'IV':4,
    'V':5,
    'VI':6,
}

class SemesterLaTeXLoader():
    def check_latex():
        pass

    def remove_latex_comments(text):
        text = re.sub(r'\\begin\{comment\}.*?\\end\{comment\}','',text, flags=re.S)
        return re.sub(r'^%.*$',r'',text,flags=re.M)

    def create_semester_db():
        pass

    def export_semester_json():
        pass

    def load_kricky(file_name,json_file=None):
        with open(file_name, 'r', encoding='utf8') as input_tex:
            text = input_tex.read()
            text = SemesterLaTeXLoader.remove_latex_comments(text)
            problems = re.findall(r'\\newcommand\{\\zad([^\{\}]+)s([^\{\}]+)\}\{(.*?)\}[^\{\}]*(?=\\newcommand|$)',text,flags=re.S)
            return [(roman_numerals[problem_serie],roman_numerals[problem_order],problem_text.strip('\n')) for problem_order, problem_serie, problem_text in problems ]
            

    def load_strom(file_name):
        with open(file_name, 'r', encoding='utf8') as input_tex:
            text = input_tex.read()
            text = SemesterLaTeXLoader.remove_latex_comments(text)
            problems = re.findall(r'(\\ifcase\\numexpr\\value\{uloha\}-1|\\or).*?\{(.*?)\}[^\{\}]*?(?=\\fi|$|\\or)',text,flags=re.S)
            semester = []
            for i,problem in enumerate(problems):
                semester.append(((i//7)+1,(i%6)+1,problem[1].strip('\n')))
            return semester

if __name__=='__main__':
    x = SemesterLaTeXLoader.load_strom('ul1.tex')
    print(x)

