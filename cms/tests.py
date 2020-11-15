<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
=======
>>>>>>> Stashed changes
'''
name of the test file must start with test
more info  here https://docs.djangoproject.com/en/3.1/topics/testing/overview/
you run them by running "./manage.py test"
'''
from django.test import TestCase
from django.test import Client
from test_utils import get_app_fixtures


class TestPosts(TestCase):
    '''test posts functionality'''
    fixtures = get_app_fixtures([
        'base',
        'cms',
    ])

    def setUp(self):
        '''create client'''
        self.client = Client()

    def test_get_status_code_visible(self):
        '''post/visible status code is 200'''
        response = self.client.get('/cms/post/visible', {}, 'json')
        self.assertEqual(response.status_code, 200)

    def test_get_(self):
        '''post status code is 403'''
        response = self.client.get('/cms/post', {}, 'json')
        self.assertEqual(response.status_code, 403)

    def test_get_response_format(self):
        '''returned object has good expected keys'''
        response_json = self.client.get('/cms/post/visible', {}, 'json').json()
        expected_keys = [
            'id',
            'links',
            'caption',
            'short_text',
            'details',
            'added_at',
            'show_after',
            'disable_after'
        ]
        self.assertTrue(len(response_json) > 0)
        for key in expected_keys:
            self.assertIn(key, response_json[0])
<<<<<<< Updated upstream
=======
    
class TestMenuItems(TestCase):
    '''test menu_items functionality'''
    fixtures = get_app_fixtures([
        'base',
        'cms',
    ])

    def setUp(self):
        '''create client'''
        self.client = Client()

    def test_get_status_code_on_current_site(self):
        '''menu-item/on-current-site status code is 200'''
        response = self.client.get('/cms/menu-item/on-current-site', {}, 'json')
        self.assertEqual(response.status_code, 200)

    def test_get_(self):
        '''menu-item status code is 200'''
        response = self.client.get('/cms/menu-item', {}, 'json')
        self.assertEqual(response.status_code, 200)
>>>>>>> Stashed changes
>>>>>>> Stashed changes
