from django.contrib import admin
from problem_database import models


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'name'
    )
