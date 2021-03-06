from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from problem_database import models
from problem_database import serializers


class TestSeminar(TestCase):

    def setUp(self):
        return models.Seminar.objects.create(name='Malynár')

    def test_seminar_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, models.Seminar))
        self.assertEqual(mod.__str__(), 'Malynár')


class SeminarViewsTest(APITestCase):

    def setUp(self):
        self.seminars = [models.Seminar.objects.create(name="Malynár"),
                         models.Seminar.objects.create(name="Matik"),
                         models.Seminar.objects.create(name="Strom")]

    URL_PREFIX = '/problem_database/seminars'

    def test_can_browse_all_seminars(self):
        response = self.client.get(self.URL_PREFIX, {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(self.seminars), len(response.data))

        for seminar in self.seminars:
            self.assertIn(
                serializers.SeminarSerializer(instance=seminar).data,
                response.data
            )


class TestActivityType(TestCase):

    def setUp(self):
        seminar = models.Seminar.objects.create(name='Malynár')
        return models.ActivityType.objects.create(name='Mamut', seminar=seminar)

    def test_activity_type_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, models.ActivityType))
        self.assertEqual(mod.__str__(), 'Mamut')


class ActivityTypeViewsTest(APITestCase):

    def setUp(self):
        seminar1 = models.Seminar.objects.create(name='Malynár')
        seminar2 = models.Seminar.objects.create(name='Matik')
        self.activity_types = [models.ActivityType.objects.create(name="Malynár", seminar=seminar1),
                               models.ActivityType.objects.create(
                                   name="Mamut", seminar=seminar1),
                               models.ActivityType.objects.create(
                                   name="Lomihlav", seminar=seminar2)]

    URL_PREFIX = '/problem_database/activity_types'

    def test_can_browse_all_activity_types(self):
        response = self.client.get(self.URL_PREFIX, {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(self.activity_types), len(response.data))

        for activity_type in self.activity_types:
            self.assertIn(
                serializers.ActivityTypeSerializer(
                    instance=activity_type).data,
                response.data
            )

    def test_filter_activity_types(self):
        response = self.client.get(self.URL_PREFIX + '/?seminar=2', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))

        self.assertIn(
            serializers.ActivityTypeSerializer(
                instance=self.activity_types[2]).data,
            response.data
        )

        response = self.client.get(self.URL_PREFIX + '/?seminar=1', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        for activity_type in self.activity_types[:2]:
            self.assertIn(
                serializers.ActivityTypeSerializer(
                    instance=activity_type).data,
                response.data
            )


class TestActivity(TestCase):

    def setUp(self):
        seminar = models.Seminar.objects.create(name='Malynár')
        activity_type = models.ActivityType.objects.create(
            name='Mamut', seminar=seminar)
        return models.Activity.objects.create(
            date='2020-06-20',
            activity_type=activity_type,
            description='Mamut 2020')

    def test_activity_type_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, models.Activity))
        self.assertEqual(mod.__str__(), 'Mamut 2020')


class TestProblemTag(TestCase):

    def setUp(self):
        problem = models.Problem.objects.create(
            problem='Lorem?', result='Ipsum')
        tag = models.Tag.objects.create(name='Výroková logika')
        return models.ProblemTag.objects.create(problem=problem, tag=tag)

    def test_problem_tag_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, models.ProblemTag))
        self.assertEqual(mod.__str__(), 'Lorem?, Výroková logika')


class ProblemTagTest(APITestCase):

    def setUp(self):
        problems = [
            models.Problem.objects.create(
                problem='Koľko je 1+2?', result='3', solution='indukciou'),
            models.Problem.objects.create(
                problem='Koľko je 2+3?', result='5', solution='priamo')
        ]
        tags = [
            models.Tag.objects.create(name='Indukcia'),
            models.Tag.objects.create(name='Aritmetika')
        ]
        self.problem_tags = [
            models.ProblemTag.objects.create(problem=problems[0], tag=tags[0]),
            models.ProblemTag.objects.create(problem=problems[0], tag=tags[1]),
            models.ProblemTag.objects.create(problem=problems[1], tag=tags[1])
        ]

    URL_PREFIX = '/problem_database/problem_tags'

    def test_can_browse_all_problem_tags(self):
        response = self.client.get(self.URL_PREFIX, {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(self.problem_tags), len(response.data))

        for problem_tag in self.problem_tags:
            self.assertIn(
                serializers.ProblemTagSerializer(instance=problem_tag).data,
                response.data
            )

    def test_filter_problem_tags(self):
        response = self.client.get(self.URL_PREFIX + '/?problem=1', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        for problem_tag in self.problem_tags[:2]:
            self.assertIn(
                serializers.ProblemTagSerializer(instance=problem_tag).data,
                response.data
            )

        response = self.client.get(self.URL_PREFIX + '/?tag=1', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))

        self.assertIn(
            serializers.ProblemTagSerializer(
                instance=self.problem_tags[0]).data,
            response.data
        )
