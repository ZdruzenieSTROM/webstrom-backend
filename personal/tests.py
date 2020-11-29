from django.test import TestCase
from user.models import User
from personal.models import Profile, School, District, County


class TestProfile(TestCase):
    def setUp(self):
        c = County.objects.create(name="Testovací kraj")
        d = District.objects.create(name="Testovací okres", county=c)
        School.objects.create(name="Testovacia škola", district=d)

    def test_create_user_without_profile(self):
        u = User()
        u.save()

        self.assertTrue(hasattr(u, 'profile'),
                        msg="Profile pre Usera nebol vytvorený automaticky.")
