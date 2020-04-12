from django.contrib import admin

from competition.models import Competition, Problem, Semester, Series

admin.site.register(Competition)
admin.site.register(Semester)
admin.site.register(Series)
admin.site.register(Problem)
