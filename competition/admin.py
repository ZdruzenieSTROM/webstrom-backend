from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from competition.models import (Competition, Event, EventRegistration, Grade,
                                LateTag, Problem, Publication, School,
                                Semester, SemesterPublication, Series, Solution,
                                UnspecifiedPublication)


@admin.register(SemesterPublication)
class SemesterPublicationAdmin(admin.ModelAdmin):
    change_form_template = 'competition/admin/semesterpublication_change.html'

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

        return super(SemesterPublicationAdmin, self).response_change(request, obj)


@admin.register(UnspecifiedPublication)
class UnspecifiedPublicationAdmin(admin.ModelAdmin):
    change_form_template = 'competition/admin/unspecifiedpublication_change.html'

    def response_change(self, request, obj):
        if 'generate-name' in request.POST:
            obj.generate_name(forced=True)

            if obj.name:
                self.message_user(request, 'Meno bolo vygenerované')
            else:
                self.message_user(
                    request, 'Meno sa nepodarilo vygenerovať', level=messages.ERROR)

            return HttpResponseRedirect('.')

        return super(UnspecifiedPublicationAdmin, self).response_change(request, obj)


admin.site.register(Competition)
admin.site.register(Event)
admin.site.register(Grade)
admin.site.register(Semester)
admin.site.register(Series)
admin.site.register(Problem)
admin.site.register(EventRegistration)
admin.site.register(Solution)
admin.site.register(LateTag)
admin.site.register(School)
