from django.contrib import admin

from personal.models import OtherSchoolRequest, School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'street',
        'city',
        'abbreviation',
    )


@admin.register(OtherSchoolRequest)
class OtherSchoolRequestAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'school_info'
    )
