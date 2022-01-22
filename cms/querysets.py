from django.db import models
from django.utils import timezone


class VisibleQuerySet(models.QuerySet):
    def visible(self, date=None):
        if date is None:
            date = timezone.now()
        return self.filter(show_after_lt=date, disable_after_gt=date)
