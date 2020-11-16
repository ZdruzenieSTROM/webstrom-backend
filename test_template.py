'''
name of the test file must start with test
more info  here https://docs.djangoproject.com/en/3.1/topics/testing/overview/
you run them by running "./manage.py test"
'''
from django.test import TestCase
from test_utils import get_app_fixtures


class TestTest(TestCase):
    '''
    test class must be a subclass of django.test.TestCase
    add fixtures to fill the db
    '''
    fixtures = get_app_fixtures([
        'base',
        'cms',
    ])

    def setUp(self):
        '''setUp method is called once before other tests'''

    def test_name_must_start_with_test(self):
        '''name of test method must start with "test_"'''
        self.assertFalse(1 + 2 == 300)

    def test_another_one(self):
        '''some test, bla, bla'''
        self.assertEqual('banan'[0], 'b')
