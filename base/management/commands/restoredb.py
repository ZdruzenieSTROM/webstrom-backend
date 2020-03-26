import os

from django.conf import settings
from django.core.management import BaseCommand, call_command

APP_PYCACHE_DIRS = ['', 'migrations', os.path.join('management', 'commands')]


def remove_contents(dir, exclude=()):
    if not os.path.exists(dir):
        return

    for file in os.listdir(dir):
        if file in exclude:
            continue
        os.remove(os.path.join(dir, file))


class Command(BaseCommand):
    def handle(self, *args, **options):
        for app in settings.LOCAL_APPS:
            app_dir = os.path.join(settings.BASE_DIR, app.split('.')[0])

            migrations_dir = os.path.join(app_dir, 'migrations')
            remove_contents(migrations_dir, exclude=[
                            '__init__.py', '__pycache__'])

            pycache_dirs = [os.path.join(app_dir, pycache_dir, '__pycache__')
                            for pycache_dir in APP_PYCACHE_DIRS]
            for pycache_dir in pycache_dirs:
                remove_contents(pycache_dir)

        database = settings.DATABASES['default'].get('NAME', None)

        if os.path.exists(database):
            os.remove(database)

        call_command('makemigrations')
        call_command('migrate')
