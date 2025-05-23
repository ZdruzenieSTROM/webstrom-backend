from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

# from user.models import User
from personal.models import County, District, School
from personal.serializers import (CountySerializer, DistrictSerializer,
                                  SchoolSerializer)


class TestProfile(TestCase):

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        district = District.objects.create(
            name="Testovací okres", county=county)
        School.objects.create(name="Testovacia škola", district=district)

    # def test_create_user_without_profile(self):
    #     user = User()
    #     user.save()

    #     self.assertTrue(hasattr(user, 'profile'),
    #                     msg="Profile pre Usera nebol vytvorený automaticky.")


class TestCounty(TestCase):
    '''
    county create
    '''

    def setUp(self):
        return County.objects.create(name='Testovaci kraj')

    def test_county_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, County))
        self.assertEqual(str(mod), 'Testovaci kraj')


class CountyViewsTest(APITestCase):
    '''
    personal/counties
    '''

    def setUp(self):
        self.counties = [County.objects.create(name="Košický kraj"),
                         County.objects.create(name="Prešovský kraj"),
                         County.objects.create(name="Bratislavský kraj")]

    URL_PREFIX = '/api/personal/counties'

    def test_can_browse_all_counties(self):
        response = self.client.get(self.URL_PREFIX, {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(self.counties), len(response.data))

        for county in self.counties:
            self.assertIn(
                CountySerializer(instance=county).data,
                response.data
            )


class TestDistrict(TestCase):
    '''
    district create
    '''

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        return District.objects.create(name='Testovaci okres', county=county)

    def test_district_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, District))
        self.assertEqual(str(mod), 'Testovaci okres')


class DistrictViewsTest(APITestCase):
    '''
    personal/district
    '''

    def setUp(self):
        county1 = County.objects.create(name="Košický kraj")
        county2 = County.objects.create(name="Prešovský kraj")
        self.districts = [District.objects.create(name="Gelnica", county=county1),
                          District.objects.create(
                              name="Rožňava", county=county1),
                          District.objects.create(name="Sabinov", county=county2)]

    URL_PREFIX = '/api/personal/districts'

    def test_can_browse_all_districts(self):
        response = self.client.get(self.URL_PREFIX, {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(self.districts), len(response.data))

        for district in self.districts:
            self.assertIn(
                DistrictSerializer(instance=district).data,
                response.data
            )

    def test_filter_districts(self):
        response = self.client.get(self.URL_PREFIX + '/?county=1', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        for district in self.districts[:2]:
            self.assertIn(
                DistrictSerializer(instance=district).data,
                response.data
            )

        response = self.client.get(self.URL_PREFIX + '/?county=2', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertIn(
            DistrictSerializer(instance=self.districts[2]).data,
            response.data
        )


class TestSchoolWithoutAddress(TestCase):
    '''
    school without address create
    '''

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        district = District.objects.create(
            name="Testovací okres", county=county)
        return School.objects.create(name='Gymnázium, Poštová 9', district=district)

    def test_school_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(str(mod), 'Gymnázium, Poštová 9')


class TestSchoolWithAddress(TestCase):
    '''
    school with address create
    '''

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        district = District.objects.create(
            name="Testovací okres", county=county)
        return School.objects.create(
            name='Gymnázium',
            district=district,
            street='Poštová 9',
            city='Košice',
            zip_code='04001'
        )

    def test_school_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(str(mod), 'Gymnázium, Poštová 9, Košice')

    def test_printable_zip_code(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(mod.printable_zip_code, '040 01')

    def test_stitok(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(
            mod.stitok, '\\stitok{Gymnázium}{Košice}{040 01}{Poštová 9}')


class SchoolViewsTest(APITestCase):
    '''
    personal/school
    '''

    def setUp(self):
        county = County.objects.create(name="Košický kraj")
        district1 = District.objects.create(name="Košice I", county=county)
        district2 = District.objects.create(name="Košice IV", county=county)
        self.schools = [
            School.objects.create(
                name='Gymnázium',
                district=district1,
                street='Poštová 9',
                city='Košice',
                zip_code='04001'
            ),
            School.objects.create(
                name='Gymnázium',
                district=district2,
                street='Alejová 1',
                city='Košice',
                zip_code='04149'
            ),
            School.objects.create(
                name='Gymnázium',
                district=district2,
                street='Opatovská cesta 7',
                city='Košice',
                zip_code='04001'
            )
        ]

    URL_PREFIX = '/api/personal/schools'

    def test_can_browse_all_schools(self):
        response = self.client.get(self.URL_PREFIX, {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(self.schools), len(response.data))

        for school in self.schools:
            self.assertIn(
                SchoolSerializer(instance=school).data,
                response.data
            )

    def test_filter_schools(self):
        response = self.client.get(
            self.URL_PREFIX + '/?district=1', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertIn(
            SchoolSerializer(instance=self.schools[0]).data,
            response.data
        )

        response = self.client.get(
            self.URL_PREFIX + '/?district=2', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        for school in self.schools[1:]:
            self.assertIn(
                SchoolSerializer(instance=school).data,
                response.data
            )

    def test_search_schools(self):
        response = self.client.get(
            self.URL_PREFIX + '/?search=Opatov', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertIn(
            SchoolSerializer(instance=self.schools[2]).data,
            response.data
        )

        response = self.client.get(
            self.URL_PREFIX + '/?search=Gym', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, len(response.data))

        for school in self.schools:
            self.assertIn(
                SchoolSerializer(instance=school).data,
                response.data
            )

        response = self.client.get(
            self.URL_PREFIX + '/?search=ová', {}, 'json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        for school in self.schools[:2]:
            self.assertIn(
                SchoolSerializer(instance=school).data,
                response.data
            )
