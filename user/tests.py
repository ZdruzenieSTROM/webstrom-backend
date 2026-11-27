from unittest.mock import patch

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from competition.models import Grade
from personal.models import County, District, OtherSchoolRequest, Profile, School
from user.models import User


@patch('user.serializers.send_bulk_html_emails')
class UserDetailsOtherSchoolTest(APITestCase):
    '''
    PATCH api/user/user/ so zvolenou "Inou školou"
    '''

    def setUp(self):
        county = County.objects.create(name='Testovací kraj')
        district = District.objects.create(
            name='Testovací okres', county=county)
        self.other_school = School.objects.create(
            code=settings.OTHER_SCHOOL_CODE, name='Iná škola', district=district)
        self.grade = Grade.objects.create(
            name='1. ročník SŠ', tag='S1', years_until_graduation=4,
            is_active=True)
        self.user = User.objects.create(email='test@strom.sk')
        self.profile = Profile.objects.create(
            user=self.user, first_name='Test', last_name='Testovací',
            school=self.other_school,
            year_of_graduation=self.grade.get_year_of_graduation_by_date())
        self.client.force_authenticate(self.user)
        self.url = reverse('user:rest_user_details')

    def patch_other_school(self, description):
        return self.client.patch(self.url, {
            'profile': {
                'first_name': 'Test',
                'last_name': 'Testovací',
                'school': self.other_school.pk,
                'grade': self.grade.pk,
            },
            'new_school_description': description,
        }, format='json')

    def test_creates_other_school_request(self, _send_mail):
        response = self.patch_other_school('Gymnázium Testovacie')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            OtherSchoolRequest.objects.get(profile=self.profile).school_info,
            'Gymnázium Testovacie')

    def test_updates_existing_other_school_request(self, _send_mail):
        # Regresia #654: zmena popisu školy padala na IntegrityError
        OtherSchoolRequest.objects.create(
            profile=self.profile, school_info='Pôvodná škola')

        response = self.patch_other_school('Nová škola')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(OtherSchoolRequest.objects.count(), 1)
        self.assertEqual(
            OtherSchoolRequest.objects.get(profile=self.profile).school_info,
            'Nová škola')
