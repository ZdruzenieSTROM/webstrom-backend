from django.test import TestCase
from user.models import User
from personal.models import School, District, County


class TestProfile(TestCase):
    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        district = District.objects.create(
            name="Testovací okres", county=county)
        School.objects.create(name="Testovacia škola", district=district)

    def test_create_user_without_profile(self):
        user = User()
        user.save()

        self.assertTrue(hasattr(user, 'profile'),
                        msg="Profile pre Usera nebol vytvorený automaticky.")
