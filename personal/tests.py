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
    
class TestCounty(TestCase):

    def setUp(self):
        return County.objects.create(name='Testovaci kraj')

    def test_county_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, County))
        self.assertEqual(mod.__str__(), 'Testovaci kraj')

class TestDistrict(TestCase):

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        return District.objects.create(name='Testovaci okres',county=county)

    def test_district_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, District))
        self.assertEqual(mod.__str__(), 'Testovaci okres')

class TestSchoolWithoutAddress(TestCase):

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        district = District.objects.create(name="Testovací kraj",county=county)
        return School.objects.create(name='Gymnázium, Poštová 9',district=district)

    def test_school_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(mod.__str__(), 'Gymnázium, Poštová 9')

class TestSchoolWithAddress(TestCase):

    def setUp(self):
        county = County.objects.create(name="Testovací kraj")
        district = District.objects.create(name="Testovací kraj",county=county)
        return School.objects.create(name='Gymnázium',district=district,street='Poštová 9',city='Košice',zip_code='04001')

    def test_school_check_title(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(mod.__str__(), 'Gymnázium, Poštová 9, Košice')
    
    def test_printable_zip_code(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(mod.printable_zip_code, '040 01')

    def test_stitok(self):
        mod = self.setUp()
        self.assertTrue(isinstance(mod, School))
        self.assertEqual(mod.stitok, '\\stitok{Gymnázium}{Košice}{040 01}{Poštová 9}')
