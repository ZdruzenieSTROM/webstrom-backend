from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from user.models import User

from user.serializers import UserShortSerializer
from personal.models import County, District, School, Profile

class UpdateUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="ucastnik@gmail.com", password="1234abcd")

        county = County.objects.create(name="Košický kraj")
        district = District.objects.create(name="Košice I", county=county)
        school = School.objects.create(name='Gymnázium', district=district, street='Poštová 9', city='Košice', zip_code='04001') 

        self.profile = Profile.objects.create(
            first_name='Účastník', last_name='Matikovský', user = self.user, 
            nickname = 'ucastnik', school = school, year_of_graduation = 2025, 
            phone = '+421901234567', parent_phone = '+421987654321', gdpr = True
        )

        #self.superuser = User.objects.create_superuser('veduci','1234abcd')
        #self.veduci_log_in = {'username':'veduci', 'password':'1234abcd'}
        #self.client.post('/user/login/',self.veduci_log_in)

        self.data = UserShortSerializer(self.user).data
        self.data.update({'first_name': 'Meno', 'last_name': 'Priezvisko'})
        self.log_in = {'username':'ucastnik', 'password':'1234abcd'}

    def test_can_update_user(self):
        response_log_in = self.client.post('/user/login/',self.log_in)
        self.assertEqual(response_log_in.status_code, 200)
        response = self.client.post('/user/profile/update/', self.data)
        self.assertEqual(response.status_code, 200)
