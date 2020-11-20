import os
from pathlib import Path

from webstrom.settings import BASE_DIR


def get_app_fixtures(app_list):
    '''returns all .json fixtures from given list of apps'''
    fixtures = []

    for app in app_list:
        fixtures_dir = os.path.join(BASE_DIR, app, 'fixtures')
        fixtures_files = map(str, Path(fixtures_dir).rglob('*.json'))
        for file in fixtures_files:
            fixtures.append(file)

    return fixtures
