import magic
from django.core.files import File


def mime_type(file: File) -> str:
    """Zistí mime type zadaného súboru"""

    # Podľa dokumentácie python-magic by mali prvé dva kB
    # spoľahlivo stačiť na určenie typu
    file.open(mode='rb')
    return magic.from_buffer(file.read(2048), mime=True)
