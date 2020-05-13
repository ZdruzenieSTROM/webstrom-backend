import os
from functools import partial

from django.conf import settings
from django.core.management import BaseCommand, call_command

APP_PYCACHE_DIRS = ['', 'migrations', os.path.join('management', 'commands')]


def remove_contents(path, exclude=()):
    if not os.path.exists(path):
        return

    for file in os.listdir(path):
        full_path = os.path.join(path, file)

        if file in exclude or os.path.isdir(full_path):
            continue

        os.remove(os.path.join(full_path))


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write('Do not run this command with DEBUG=False')
            return

        for app in settings.LOCAL_APPS:
            app_dir = os.path.join(settings.BASE_DIR, app.split('.')[0])

            pycache_dirs = [os.path.join(app_dir, pycache_dir, '__pycache__')
                            for pycache_dir in APP_PYCACHE_DIRS]
            for pycache_dir in pycache_dirs:
                remove_contents(pycache_dir)

            migrations_dir = os.path.join(app_dir, 'migrations')
            remove_contents(migrations_dir, exclude=['__init__.py'])

        remove_contents(os.path.join(
            settings.BASE_DIR, 'webstrom', '__pycache__'))

        database = settings.DATABASES['default'].get('NAME', '')

        if os.path.exists(database):
            os.remove(database)

        call_command('makemigrations')
        call_command('migrate')

        load_fixture = partial(call_command, 'loaddata')

        load_fixture('sites', 'flatpages')

        load_fixture('counties', 'districts', 'schools', 'schools_custom')
        load_fixture('superuser', 'groups', 'users', 'profiles')
        load_fixture('users_random', 'profiles_random')

        load_fixture('competitions', 'grades', 'late_tags')
        load_fixture('semesters', 'event_registrations')
        load_fixture('event_registrations_random', 'solutions_random')
