
from django.db.models import QuerySet
from django.utils.timezone import now


class VisibilityQuerySet(QuerySet):
    def visible(self):
        today = now()
        return self.filter(visible_after__lte=today, visible_until__gte=today)
