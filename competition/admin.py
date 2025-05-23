from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from competition.models import (Comment, Competition, Event, EventRegistration,
                                Grade, LateTag, Problem, ProblemCorrection,
                                Publication, RegistrationLink, Semester,
                                Series, Solution)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tag',
        'years_until_graduation',
        'is_active'
    )


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_year',
        'competition_type'
    )


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
    )

    @staticmethod
    def complete(obj: Series):
        return obj.complete
    complete.boolean = True
    complete.admin_order_field = 'complete'

    @staticmethod
    def active(obj: Series):
        return not obj.is_past_deadline
    active.boolean = True

    @staticmethod
    def competition(obj: Series):
        return obj.semester.competition
    competition.admin_order_field = 'semester__competition'


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
        return obj.semester_registration.profile.get_full_name()\
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
        'state',
        'hidden_response'
    )

    list_filter = (
        'posted_by',
        'problem',
        'state',
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
        'profile',
        'school',
        'grade',
        'event',
    )

    ordering = (
        'event',
    )


@admin.register(RegistrationLink)
class RegistrationLinkAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'start',
        'end'
    )


@admin.register(ProblemCorrection)
class ProblemCorrectionAdmin(admin.ModelAdmin):
    list_display = (
        'problem',
    )

    list_filter = (
        'problem',
    )


@admin.register(LateTag)
class LateTagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'upper_bound'
    )
