import magic
from django.core.files import File


def mime_type(file: File) -> str:
    """Zistí mime type zadaného súboru"""

    return magic.from_buffer(file.read(2048), mime=True)
