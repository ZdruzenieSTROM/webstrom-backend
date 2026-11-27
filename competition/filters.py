

import unicodedata

from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import Func, Q
from django.db.models.functions import Lower
from django.db.models.manager import BaseManager
from django.utils.timezone import now
from django_filters import BooleanFilter
from rest_framework.filters import BaseFilterBackend, SearchFilter


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


class CanUserModifyFilter(BaseFilterBackend):
    """
    Pri query parametri `can_modify=true` vráti iba objekty, ktoré vie
    aktuálny používateľ editovať.

    Logiku poskytuje model cez classmethod `filter_modifiable(queryset, user)`,
    ktorá je queryset verziou `can_user_modify` (kaskáda na rodiča až po súťaž).
    """
    query_param = 'can_modify'
    TRUE_VALUES = {'true', '1', 'yes', 'on'}

    def filter_queryset(self, request, queryset, view):
        value = request.query_params.get(self.query_param)
        if value is None or value.lower() not in self.TRUE_VALUES:
            return queryset

        filter_modifiable = getattr(queryset.model, 'filter_modifiable', None)
        if filter_modifiable is None:
            raise ImproperlyConfigured(
                f'{queryset.model.__name__} nemá metódu filter_modifiable')
        return filter_modifiable(queryset, request.user)
