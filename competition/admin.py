from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.db.models import Value, CharField, F

from competition.models import (Competition, Event, EventRegistration, Grade,
                                LateTag, Problem, Publication, School,
                                Semester, Series, Solution)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'street', 'city', 'abbreviation']


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'order', 'series', 'get_text']
    def get_text(self, obj):
        return obj.text[:70]+'...'

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ['solutionName', 'problem', 'semester_registration', 'uploaded_at', 'late_tag', 'is_online', 'score']
    list_editable = ['score']

    date_hierarchy = 'uploaded_at'

    def solutionName(self, obj):
        return str(obj.semester_registration.profile.user.get_full_name())+' | '+str(obj.problem.order)

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    change_form_template = 'competition/admin/publication_change.html'

    list_display = ['thumb', 'name', 'comp', 'event', 'order']
    ordering = ['event', '-order']

    list_filter = ['event']

    def comp(self, obj):
        return obj.event.competition
    comp.__name__ = 'competition'


    def thumb(self, obj):
        return format_html("<a href='{}'><img src='{}' height='100' /></a>", obj.thumbnail.url, obj.thumbnail.url)
    
    def response_change(self, request, obj):
        if 'generate-name' in request.POST:
            obj.generate_name(forced=True)

            if obj.name:
                self.message_user(request, 'Meno bolo vygenerované')
            else:
                self.message_user(
                    request, 'Meno sa nepodarilo vygenerovať', level=messages.ERROR)

            return HttpResponseRedirect('.')

        if 'generate-thumbnail' in request.POST:
            obj.generate_thumbnail(forced=True)

            if obj.thumbnail:
                self.message_user(request, 'Náhľad bol vygenerovaný')
            else:
                self.message_user(
                    request, 'Náhľad sa nepodarilo vygenerovať', level=messages.ERROR)

            return HttpResponseRedirect('.')

        return super(PublicationAdmin, self).response_change(request, obj)


admin.site.register(Event)
admin.site.register(Semester)
admin.site.register(Series)
admin.site.register(EventRegistration)
#admin.site.register(Competition)
#admin.site.register(Grade)
#admin.site.register(LateTag)
