from django.contrib import admin

from competition.models import Competition, Event, Grade, Problem, Semester, Series, UserEventRegistration, Publication, Solution, LateTag

admin.site.register(Competition)
admin.site.register(Event)
admin.site.register(Grade)
admin.site.register(Semester)
admin.site.register(Series)
admin.site.register(Problem)
admin.site.register(Publication)
admin.site.register(UserEventRegistration)
admin.site.register(Solution)
admin.site.register(LateTag)
