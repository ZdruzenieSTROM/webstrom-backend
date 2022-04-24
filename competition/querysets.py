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

    def upcoming_or_current(self, date=None):
        """Najbližšia alebo aktuálna akcia"""
        if date is None:
            date = timezone.now()
        return self.filter(end__gte=date).earliest('end')

    def history(self, date=None):
        "Akcie ktoré sú už ukončnené"
        if date is None:
            date = timezone.now()
        return self.filter(end__lt=date).order_by('-end')

    def current(self, date=None):
        """Aktuálny semester na zobrazenie"""
        if date is None:
            date = timezone.now()
        return self.filter(start__lt=date).order_by('-end').first()
