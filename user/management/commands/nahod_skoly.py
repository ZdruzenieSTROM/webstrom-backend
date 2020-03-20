import os
from csv import DictReader

from django.core.management import BaseCommand, CommandError

from user.models import Kraj, Okres, Skola

SCHOOLS_DIR = 'user/management/skoly'


class Command(BaseCommand):
    def handle(self, *args, **options):
        # TODO: premyslieť oznamovanie duplikátov
        # TODO: veľa duplikátneho kódu, vymyslieť ako sa ho zbaviť

        with open(os.path.join(SCHOOLS_DIR, 'kraje.csv')) as kraje:
            reader = DictReader(kraje)

            for kraj in reader:
                if Kraj.objects.filter(**kraj).exists():
                    self.stdout.write(f'{ kraj["nazov"] } už existuje')
                else:
                    Kraj.objects.create(**kraj)

        with open(os.path.join(SCHOOLS_DIR, 'okresy.csv')) as okresy:
            reader = DictReader(okresy)

            for okres in reader:
                okres['kraj'] = Kraj.objects.get(kod=okres['kraj'])

                if Okres.objects.filter(**okres).exists():
                    self.stdout.write(f'{ okres["nazov"] } už existuje')
                else:
                    Okres.objects.create(**okres)

        with open(os.path.join(SCHOOLS_DIR, 'skoly.csv')) as skoly:
            reader = DictReader(skoly)

            for skola in reader:
                skola['okres'] = Okres.objects.get(kod=skola['okres'])

                if Skola.objects.filter(**skola).exists():
                    self.stdout.write(f'{ skola["nazov"] } už existuje')
                else:
                    Skola.objects.create(**skola)
