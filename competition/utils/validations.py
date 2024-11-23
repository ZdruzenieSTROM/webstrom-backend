from django.core.exceptions import ValidationError


def validate_points(value: int):
    if value < 0 or value > 9:
        raise ValidationError(
            f'{value} je mimo povoleného rozmedzia pre body. Povolený rozsah je 0-9.'
        )
