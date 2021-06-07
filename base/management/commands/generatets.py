from django_typomatic import generate_ts

from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_ts('./apiTypes.ts',trim_serializer_output=True)
