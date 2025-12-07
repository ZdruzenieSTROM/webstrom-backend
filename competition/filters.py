

import unicodedata

from django.db import connection
from django.db.models import Func, Q
from django.db.models.functions import Lower
from django.db.models.manager import BaseManager
from django.utils.timezone import now
from django_filters import BooleanFilter
from rest_framework.filters import SearchFilter


class UpcomingFilter(BooleanFilter):
    def filter(self, qs: BaseManager, value: bool):
        if value is None:
            return qs
        lookup_expr = 'gte' if value else 'lte'
        lookup = '__'.join([self.field_name, lookup_expr])
        return qs.filter(**{lookup: now()})


class Unaccent(Func):
    function = 'unaccent'
    template = "%(function)s(%(expressions)s::text)"

    def __rand__(self, other):
        raise NotImplementedError(
            "Not supported"
        )

    def __ror__(self, other):
        raise NotImplementedError(
            "Not supported"
        )

    def __rxor__(self, other):
        raise NotImplementedError(
            "Not supported"
        )


class UnaccentSearchFilter(SearchFilter):

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset

        engine = connection.vendor

        for term in search_terms:
            term_filter = Q()
            for field in self.get_search_fields(view, request):

                if engine == 'postgresql':
                    normalized_term = ''.join(
                        c for c in unicodedata.normalize('NFKD', term)
                        if not unicodedata.combining(c)
                    ).lower()
                    normalized_field = f'normalized_{field.replace(".", "_")}'
                    if normalized_field not in queryset.query.annotations:
                        queryset = queryset.annotate(**{
                            normalized_field: Lower(Unaccent(field))
                        })
                    term_filter |= Q(
                        **{f"{normalized_field}__icontains": normalized_term})

                else:
                    # Fallback: simple icontains - SQLite does not support unaccent
                    term_filter |= Q(**{f"{field}__icontains": term})

            queryset = queryset.filter(term_filter)

        return queryset
