import json
import os
from datetime import datetime
from typing import Any, Optional

from competition.models import (Competition, Event, PublicationType,
                                UnspecifiedPublication)
from competition.utils import get_school_year_by_date
from django.core.management import BaseCommand
from django.utils.timezone import now


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('folder_path', type=str)

    def _get_dates(self, file_path):
        with open(file_path, 'r', encoding='utf-8')
        json.load()

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        folder_root = options['folder_path']
        folders = os.listdir(folder_root)
        for folder in folders:
            try:
                competition = Competition.objects.get(slug=folder)
            except Competition.DoesNotExist:
                print(f'Skipping folder `{folder}`,'
                      ' because competition with slug `{folder}` does not exist')
                continue

    def tmp(self):
        for competition in Competition.objects.all():
            if competition.competition_type.pk == 0:
                # Semesters are loaded by different command
                continue
            start = competition.start_year
            year = 1
            while start < now().year:
                if start not in self.COMPETITION_CANCELED[competition.pk]:
                    usual_date = self.COMPETITION_USUAL_DATE[competition.pk]
                    start_date = datetime(
                        start, usual_date[0][1], usual_date[0][0])
                    end_date = datetime(
                        start, usual_date[1][1], usual_date[1][0])
                    event = Event.objects.create(
                        competition=competition,
                        year=year,
                        school_year=get_school_year_by_date(
                            end_date),
                        season_code=2,
                        start=start_date,
                        end=end_date,
                    )
                    year += 1
                    if competition.competition_type.pk in [1, 3, 5]:
                        UnspecifiedPublication.objects.create(
                            name='Zadanie',
                            event=event,
                            file='media/zadania.pdf',
                            publication_type=PublicationType.objects.get(
                                name='Zadania')
                        )
                        UnspecifiedPublication.objects.create(
                            name='Poradie',
                            event=event,
                            file='media/poradie.pdf',
                            publication_type=PublicationType.objects.get(
                                name='Poradie')
                        )
                start += 1
