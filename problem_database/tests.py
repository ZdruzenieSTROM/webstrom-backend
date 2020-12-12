from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from user.models import User
from problem_database.models import Seminar
from problem_database.serializers import SeminarSerializer

class TestSeminar(TestCase):

    def setUp(self):
        return Seminar.objects.create(seminar_id=Seminar.objects.count()+1,name='Malynár')

    def test_problem_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, Seminar))
        self.assertEqual(mod.__str__(), 'Malynár')
