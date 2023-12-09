from datetime import datetime
from typing import Optional

from django.utils.timezone import now


def get_school_year_start_by_date(date: Optional[datetime] = None) -> int:
    if date is None:
        date = now()

    return date.year if date.month >= 9 else date.year - 1


def get_school_year_end_by_date(date: Optional[datetime] = None) -> int:
    return get_school_year_start_by_date(date) + 1


def get_school_year_by_date(date: Optional[datetime] = None) -> str:
    return f'{get_school_year_start_by_date(date)}/{get_school_year_end_by_date(date)}'
