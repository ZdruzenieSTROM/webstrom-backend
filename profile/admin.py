from django.contrib import admin

from profile.models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'street',
        'city',
        'abbreviation',
    )
