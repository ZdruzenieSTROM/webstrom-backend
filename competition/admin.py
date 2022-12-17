from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from competition.models import (Comment, Event, EventRegistration, Problem,
                                ProblemCorrection, Publication, Semester,
                                Series, Solution)


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

    @staticmethod
    def active(obj):
        return not obj.is_past_deadline
    active.boolean = True

    @staticmethod
    def competition(obj):
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


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'order',
        'series',
        'get_text',
    )

    @staticmethod
    def get_text(obj):
        return obj.text[:70] + '...'


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = (
        'solution_name',
        'problem',
        'semester_registration',
        'uploaded_at',
        'late_tag',
        'is_online',
        'score',
    )

    list_editable = ('score', )

    list_filter = (
        'semester_registration__event__competition',
        'late_tag',
        'is_online',
        'score',
    )

    date_hierarchy = 'uploaded_at'

    @staticmethod
    def solution_name(obj):
        return obj.semester_registration.profile.user.get_full_name()\
            + ' | ' + str(obj.problem.order)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    change_form_template = 'competition/admin/publication_change.html'

    def response_change(self, request, obj):
        if 'generate-name' in request.POST:
            obj.generate_name(forced=True)

            if obj.name:
                self.message_user(request, 'Meno bolo vygenerované')
            else:
                self.message_user(
                    request, 'Meno sa nepodarilo vygenerovať', level=messages.ERROR)

            return HttpResponseRedirect('.')

        return super().response_change(request, obj)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'problem',
        'text',
        'posted_at',
        'posted_by',
        'published',
    )

    list_filter = (
        ('posted_by', RelatedDropdownFilter),
        ('problem', RelatedDropdownFilter),
        'published',
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        # '__str__',
        'profile',
        'school',
        'grade',
        'event',
    )

    list_filter = (
        ('profile', RelatedDropdownFilter),
        ('school', RelatedDropdownFilter),
        ('grade', RelatedDropdownFilter),
        ('event', RelatedDropdownFilter),
    )

    ordering = (
        'event',
    )


@admin.register(ProblemCorrection)
class ProblemCorrectionAdmin(admin.ModelAdmin):
    list_display = (
        'problem',
    )

    list_filter = (
        ('problem', RelatedDropdownFilter),
    )
