from django.contrib import admin

from problem_database import models


@admin.register(models.ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'seminar'
    )
