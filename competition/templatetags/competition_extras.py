from django import template

register = template.Library()


@register.filter(name='score_pretty')
def score_pretty(solution):
    return '?' if solution.score is None else solution.score


@register.filter
def batch(queryset, count=1):
    for ndx in range(0, len(queryset), count):
        yield queryset[ndx:ndx+count]
