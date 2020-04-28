from django.core.exceptions import ImproperlyConfigured
from django.db import models


class UnspecifiedValueManager(models.Manager):
    """Custom manager pre modely kde vystupuje jedna hodnota ako
    'neurčená', aby sme sa nemuseli ďalej v kóde spoliehať na to
    že táto hodnota bude mať vždy nejaké konkrétne id
    """

    unspecified_value_pk = None

    def __init__(self, unspecified_value_pk, *args, **kwargs):
        self.unspecified_value_pk = self.unspecified_value_pk or \
            unspecified_value_pk

        if self.unspecified_value_pk is None:
            raise ImproperlyConfigured(
                'UnspecifiedValueManager potrebuje mať nastavené unspecified_value_pk')

        super(UnspecifiedValueManager, self).__init__(*args, **kwargs)

    def all_except_unspecified(self):
        queryset = super(UnspecifiedValueManager, self).get_queryset()
        return queryset.exclude(pk=self.unspecified_value_pk)

    def get_unspecified_value(self):
        return super(UnspecifiedValueManager, self).get_queryset().get(
            pk=self.unspecified_value_pk)

    def filter(self, *args, **kwargs):
        include_unspecified = kwargs.pop('include_unspecified', False)
        queryset = super(UnspecifiedValueManager, self).get_queryset()

        filter_results = queryset.filter(*args, **kwargs)

        if include_unspecified:
            filter_results |= queryset.filter(pk=self.unspecified_value_pk)

        return filter_results
