import os
from pathlib import Path
from rest_framework.test import APIClient
from user.models import User
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


class PermissionTestMixin:
    user_settings = {
        'competitor': {
            'verified_email': True,
            'is_staff': False,
            'is_active': True
        },
        'kricky': {
            'verified_email': True,
            'is_staff': True,
            'is_active': True
        },
        'strom': {
            'verified_email': True,
            'is_staff': True,
            'is_active': True
        }
    }

    @classmethod
    def get_basic_fixtures(cls):
        return [
            os.path.join(BASE_DIR, 'base', 'fixtures', 'sites.json'),
            os.path.join(BASE_DIR, 'competition',
                         'fixtures', 'competitions.json')
        ] + get_app_fixtures(['personal', 'user'])

    def create_users(self):
        self.competitior_user = self.create_user('competitor')
        self.kricky_user = self.create_user('kricky')
        self.strom_user = self.create_user('strom')

    def create_user(self, user_type):
        user = User.objects.create(
            email=f'{user_type}@strom.sk',
            password='1234',
            **self.user_settings[user_type])
        if user_type == 'kricky':
            user.groups.set([2])
        elif user_type == 'strom':
            user.groups.set([1])
        return user

    def get_client(self, user_type=None):
        self.client = APIClient()
        if user_type is not None:
            user = User.objects.get(email=f'{user_type}@strom.sk')
            self.client.force_authenticate(user=user)
        return self.client

    #pylint: disable=dangerous-default-value
    def check_permissions(self, url, method, responses, body={}):
        for user, status in responses.items():
            client = self.get_client(user)
            expected_response = status if isinstance(
                status, list) else [status]
            if method == 'GET':
                response = client.get(url, body, 'json')
            elif method == 'POST':
                response = client.post(url, body, 'json')
            elif method == 'PUT':
                response = client.put(url, body, 'json')
            else:
                raise NotImplementedError()
            self.assertIn(response.status_code, expected_response,
                          f'Permission assertion failed on user {user} with {method} {url}')

    PUBLIC_OK_RESPONSES = {
        'competitor': [200, 201],
        'strom': [200, 201],
        'kricky': [200, 201],
        None: [200, 201]
    }
    ONLY_STROM_OK_RESPONSES = {
        'competitor': [403, 405],
        'strom': [200, 201],
        'kricky': [403, 405],
        None: [401, 403, 405]
    }
    ONLY_KRICKY_OK_RESPONSES = {
        'competitor': [403, 405],
        'strom': [403, 405],
        'kricky': [200, 201],
        None: [401, 403, 405]}
    ALL_FORBIDDEN = {
        'competitor': [403, 405],
        'strom': [403, 405],
        'kricky': [403, 405],
        None: [401, 403, 405]
    }
    ONLY_STAFF_OK_RESPONSES = {
        'competitor': [403, 405],
        'strom': [200, 201],
        'kricky': [200, 201],
        None: [401, 403, 405]
    }
