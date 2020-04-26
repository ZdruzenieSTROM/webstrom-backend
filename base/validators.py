from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

phone_number_validator = RegexValidator(
    regex=r'^(\+\d{1,3}\s?\d{3}\s?\d{3}\s?\d{3}|\d{4}\s?\d{3}\s?\d{3})$',
    # ale prejde to tym aj bez medzier
    message='Zadaj telefónne číslo vo formáte +421 123 456 789 alebo 0912 345 678.',
)

def school_year_validator(value):
    if '/' in value:
        years = value.split('/')
        if len(years)==2 and int(years[0])+1==int(years[1]):
            return
    raise ValidationError(
            f'{value} nie je vo formáte YYYY/YYYY (napr. 2019/2020)',
        )