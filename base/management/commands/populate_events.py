from datetime import datetime
from typing import Any, Optional

from competition.models import (Competition, Event, PublicationType,
                                UnspecifiedPublication)
from competition.utils import get_school_year_by_date
from django.core.management import BaseCommand
from django.utils.timezone import now


class Command(BaseCommand):
    COMPETITION_CANCELED = {
        3: [2020, 2021],
        4: [2020, 2021],
        5: [2020, 2021],
        6: [],
        7: [],
        8: [],
        9: [2020, 2021],
        10: []
    }
    COMPETITION_USUAL_DATE = {
        3: ((31, 10), (31, 10)),
        4: ((1, 12), (1, 12)),
        5: ((1, 6), (1, 6)),
        6: ((1, 9), (1, 9)),
        7: ((1, 8), (8, 8)),
        8: ((1, 10), (1, 10)),
        9: ((1, 6), (1, 6)),
        10: ((1, 10), (1, 10))
    }

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
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
