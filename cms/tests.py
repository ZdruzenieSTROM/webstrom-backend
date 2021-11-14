from rest_framework.test import APITestCase
from tests.test_utils import get_app_fixtures, PermissionTestMixin


class TestPosts(APITestCase, PermissionTestMixin):
    '''cms/post'''

    URL_PREFIX = '/cms/post'

    fixtures = get_app_fixtures([
        'base',
        'cms',
        'personal',
        'user'
    ])

    post_expected_keys = [
        'id',
        'links',
        'caption',
        'short_text',
        'details',
        'added_at',
        'visible_after',
        'visible_until'
    ]

    def setUp(self):
        self.create_users()

    def test_get_status_code(self):
        '''status code 403'''
        self.check_permissions(self.URL_PREFIX + '/',
                               'GET', self.ONLY_STAFF_OK_RESPONSES, {})

    def test_get_specific_post(self):
        '''/0 content ok'''
        self.check_permissions(self.URL_PREFIX + '/visible',
                               'GET', self.PUBLIC_OK_RESPONSES, {})
        response = self.client.get(self.URL_PREFIX + '/visible', {}, 'json')
        self.assertEqual(response.status_code, 200)
        for key in self.post_expected_keys:
            self.assertIn(key, response.json()[0])

    def test_get_response_format(self):
        '''/visible returned object has good expected keys'''
        response_json = self.client.get(
            self.URL_PREFIX + '/visible', {}, 'json').json()
        self.assertTrue(len(response_json) > 0)
        for response in response_json:
            for key in self.post_expected_keys:
                self.assertIn(key, response)


class TestMenuItems(APITestCase, PermissionTestMixin):
    '''cms/menu-item'''

    URL_PREFIX = '/cms/menu-item'

    fixtures = get_app_fixtures([
        'base',
        'cms',
        'personal',
        'user'
    ])

    def setUp(self):
        self.create_users()

    def test_get_status_code_on_current_site(self):
        '''/on-current-site check if any'''
        response = self.client.get(
            self.URL_PREFIX + '/on-current-site', {}, 'json')
        self.check_permissions(self.URL_PREFIX + '/on-current-site',
                               'GET', self.PUBLIC_OK_RESPONSES, {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

    def test_get_status_code(self):
        '''check if any'''
        response = self.client.get(self.URL_PREFIX, {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        self.check_permissions(self.URL_PREFIX + '/',
                               'GET', self.PUBLIC_OK_RESPONSES, {})

    def test_get_status_code_specific_site(self):
        '''/1 check if any'''
        response = self.client.get(self.URL_PREFIX + '/on-site/1', {}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        self.check_permissions(self.URL_PREFIX + '/on-site/1',
                               'GET', self.PUBLIC_OK_RESPONSES, {})
