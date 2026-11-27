from django.core.exceptions import ValidationError

MIN_POINTS = -9
MAX_POINTS = 9


def validate_points(value: int):
    if not isinstance(value, int):
        raise ValidationError(
            f'{value} nie je celé číslo. Body musia býť celé číslo '
            f'v rozmedzí {MIN_POINTS} až {MAX_POINTS}.'
        )
    if value < MIN_POINTS or value > MAX_POINTS:
        raise ValidationError(
            f'{value} je mimo povoleného rozmedzia pre body. '
            f'Povolený rozsah je {MIN_POINTS} až {MAX_POINTS}.'
        )
