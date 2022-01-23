from django.db import models
from django.utils import timezone


class ActiveQuerySet(models.QuerySet):
    def active(self, date=None):
        """Iba aktívne objekty"""
        if date is None:
            date = timezone.now()
        return self.filter(
            start__lt=date, end__gt=date
        )

    def current(self, date=None):
        """Aktuálny semester na zobrazenie"""
        if date is None:
            date = timezone.now()
        return self.filter(start__lt=date).order_by('-end').first()
