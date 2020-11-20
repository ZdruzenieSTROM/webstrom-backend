'''
name of the test file must start with test
more info  here https://docs.djangoproject.com/en/3.1/topics/testing/overview/
you run them by running "./manage.py test"
'''
from django.test import TestCase
from rest_framework.test import APIClient

from tests.test_utils import get_app_fixtures


class TestTest(TestCase):
    '''
    test class must be a subclass of django.test.TestCase
        or another suitable class; visit docs for more
    add fixtures to fill the db
    '''
    fixtures = get_app_fixtures([
        'base',
        'cms',
    ])

    def setUp(self):
        '''
        setUp method is called once before other tests
        most of the time we want to use APIClient
        '''
        self.client = APIClient()

    def test_name_must_start_with_test(self):
        '''name of test method must start with "test"'''
        self.assertFalse(1 + 2 == 300)

    def test_another_one(self):
        '''some test, bla, bla'''
        self.assertEqual('banan'[0], 'b')
