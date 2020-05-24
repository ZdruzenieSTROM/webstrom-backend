from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.db.models import Value, CharField, F

from competition.models import (Competition, Event, EventRegistration, Grade,
                                LateTag, Problem, Publication, School,
                                Semester, Series, Solution)
@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'competition',
        'semester',
        'order',
        'deadline',
        'active',
        'complete',
    )

    list_filter = (
        'semester__competition',
        'complete',
    )

    def active(self, obj):
        return not obj.is_past_deadline
    active.boolean = True

    def competition(self, obj):
        return obj.semester.competition
    active.admin_order_field = 'semester__competition'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'competition',
        'year',
        'school_year',
        'start',
        'end',
    )

    list_filter = (
        'competition',
        'school_year'
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'competition',
        'year',
        'school_year',
        'season_code',
        'start',
        'end',
    )

    list_filter = (
        'competition',
        'school_year',
        'season_code',
    )

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'street', 
        'city', 
        'abbreviation',
    )


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 
        'order', 
        'series', 
        'get_text',
    )
    def get_text(self, obj):
        return obj.text[:70]+'...'

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    
    list_display = (
        'solutionName', 
        'problem', 
        'semester_registration', 
        'uploaded_at', 
        'late_tag', 
        'is_online', 
        'score'
    )
    list_editable = ('score',)

    list_filter = (
        'semester_registration__event__competition', 
        'late_tag', 
        'is_online', 
        'score',
    )

    date_hierarchy = 'uploaded_at'

    def solutionName(self, obj):
        return str(obj.semester_registration.profile.user.get_full_name())+' | '+str(obj.problem.order)

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    change_form_template = 'competition/admin/publication_change.html'

    list_display = (
        'name', 
        'thumb', 
        'competition', 
        'event', 
        'order', 
        'school_year',
    )
    ordering = (
        'event', 
        '-order',
    )

    list_filter = (
        'event__school_year', 
        'event__competition',
    )

    def school_year(self, obj):
        return obj.event.school_year
    school_year.admin_order_field = 'event__school_year'

    def competition(self, obj):
        return obj.event.competition
    competition.__name__ = 'competition'
    competition.admin_order_field = 'event__competition'
    #comp.admin_filter_field = 'event__competition'


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


#admin.site.register(EventRegistration)
#admin.site.register(Competition)
#admin.site.register(Grade)
#admin.site.register(LateTag)
