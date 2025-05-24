import os
import shutil
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

        database = settings.DATABASES['default'].get('NAME', '')

        if os.path.exists(database):
            os.remove(database)

        call_command('migrate')

        load_fixture = partial(call_command, 'loaddata')
        fixture_files = [
            (os.path.join('competition', 'fixtures', 'sources'),
             os.path.join('media', 'publications', '2022'), 'zadaniaMatboj1.pdf'),
            (os.path.join('competition', 'fixtures', 'sources'),
             os.path.join('media', 'publications', '2022'), 'poradieMatboj1.pdf'),
        ]
        for source, target, file in fixture_files:
            target_path = os.path.join(settings.BASE_DIR, target)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            shutil.copyfile(
                os.path.join(settings.BASE_DIR, source, file),
                os.path.join(target_path, file)
            )
        load_fixture('sites',
                     'flatpages',
                     'counties',
                     'districts',
                     'schools_special',
                     'schools',
                     'groups',
                     'users',
                     'publication_type',
                     'dummy_users',
                     'profiles',
                     'profiles_more',
                     'competition_types',
                     'competitions',
                     'grades',
                     'late_tags',
                     'semesters',
                     'registration_link',
                     'event_registrations',
                     'event_registrations_more',
                     'solutions',
                     'posts',
                     'post_links',
                     'menu_items',
                     'message_templates',
                     'info_banner',
                     'events'
                     )
