from django.contrib import admin

from competition.models import (Competition, Event, Grade, LateTag, Problem,
                                Publication, Semester, Series, Solution,
                                UserEventRegistration)

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
