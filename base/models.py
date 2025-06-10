from django.core.exceptions import ValidationError
from django.db import models

from base.utils import mime_type


class RestrictedFileField(models.FileField):
    """Nadstavba FileFieldu ktorá si stráži povolené typy súborov a maximálnu veľkosť"""

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', None)
        self.max_size = kwargs.pop('max_size', None)

        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        file = super().clean(*args, *kwargs)

        if self.max_size and file.size > self.max_size:
            raise ValidationError(
                'Prekročená maximálna povolená veľkosť súboru')

        if self.content_types and mime_type(file) not in self.content_types:
            raise ValidationError(
                'Nepovolený typ súboru')

        return file


class Site(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
