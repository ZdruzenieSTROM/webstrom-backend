from django.core.management import BaseCommand
from django_typomatic import generate_ts


class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_ts('./base.ts', context='base', trim_serializer_output=True)
        generate_ts('./cms.ts', context='cms', trim_serializer_output=True)
        generate_ts('./competition.ts', context='competition', trim_serializer_output=True)
        generate_ts('./personal.ts', context='personal', trim_serializer_output=True)
        generate_ts('./problem_database.ts', context='problem_database', trim_serializer_output=True)
        generate_ts('./user.ts', context='user', trim_serializer_output=True)
