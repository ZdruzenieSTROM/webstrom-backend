from django.test import TestCase
from rest_framework.test import APIClient
from tests.test_utils import get_app_fixtures


class TestPosts(TestCase):
    '''cms/post'''
    fixtures = get_app_fixtures([
        'base',
        'cms',
    ])

    post_expected_keys = [
        'id',
        'links',
        'caption',
        'short_text',
        'details',
        'added_at',
        'show_after',
        'disable_after'
    ]

    def setUp(self):
        '''create client'''
        self.client = APIClient()

    def test_get_status_code(self):
        '''status code 403'''
        response = self.client.get('/cms/post', {}, 'json')
        self.assertEqual(response.status_code, 403)

    def test_get_specific_post(self):
        '''/0 content ok'''
        response = self.client.get('/cms/post/visible', {}, 'json')
        self.assertEqual(response.status_code, 200)
        for key in self.post_expected_keys:
            self.assertIn(key, response.json()[0])

    def test_get_status_code_visible(self):
        '''/visible status code 200'''
        response = self.client.get('/cms/post/visible', {}, 'json')
        self.assertEqual(response.status_code, 200)

    def test_get_response_format(self):
        '''/visible returned object has good expected keys'''
        response_json = self.client.get('/cms/post/visible', {}, 'json').json()
        self.assertTrue(len(response_json) > 0)
        for response in response_json:
            for key in self.post_expected_keys:
                self.assertIn(key, response)


class TestMenuItems(TestCase):
    '''cms/menu-item'''
    fixtures = get_app_fixtures([
        'base',
        'cms',
    ])

    def setUp(self):
        '''create client'''
        self.client = APIClient()

    def test_get_status_code_on_current_site(self):
        '''/on-current-site status code 200'''
        response = self.client.get(
            '/cms/menu-item/on-current-site', {}, 'json')
        self.assertEqual(response.status_code, 200)

    def test_get_(self):
        '''status code 200'''
        response = self.client.get('/cms/menu-item', {}, 'json')
        self.assertEqual(response.status_code, 200)
