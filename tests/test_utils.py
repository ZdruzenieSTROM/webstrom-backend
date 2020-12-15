import os
from pathlib import Path
from user.models import User
from rest_framework.test import APIClient
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
        'unverified': {
            'verified_email': False,
            'is_staff': False,
            'is_active': False
        },
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

    def create_users(self):
        self.unverified_user = self.create_user('unverified')
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
            self.client.login(user=f'{user_type}@strom.sk')
        return self.client

    #pylint: disable=dangerous-default-value
    def check_permissions(self, url, method, responses, body={}):
        for user, expected_response in responses.items():
            client = self.get_client(user)
            if method == 'GET':
                response = client.get(url, body, 'json')
            elif method == 'POST':
                response = client.post(url, body, 'json')
            else:
                raise NotImplementedError()
            self.assertEqual(response.status_code, expected_response,
                             f'Permission assertion failed on {user} with {method} {url}')

    def check_post_public_object(self, url, body):
        responses = {user_name: 200 for user_name in self.user_settings}
        responses[None] = 200
        self.check_permissions(url, 'GET', responses, body)

    def check_post_strom_object(self, url, body):
        responses = {'unverified': 405, }
        responses = {user_name: 200 for user_name in self.user_settings}
        responses[None] = 200
        self.check_permissions(url, 'GET', responses, body)

    def check_post_kricky_object(self, url, body):
        responses = {user_name: 200 for user_name in self.user_settings}
        responses[None] = 200
        self.check_permissions(url, 'GET', responses, body)
