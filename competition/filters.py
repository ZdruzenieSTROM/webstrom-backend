from django.db.models.manager import BaseManager
from django.utils.timezone import now
from django_filters import BooleanFilter


class UpcomingFilter(BooleanFilter):
    def filter(self, qs: BaseManager, value: bool):
        lookup_expr = 'gte' if value else 'lte'
        lookup = '__'.join([self.field_name, lookup_expr])
        return qs.filter(**{lookup: now()})
