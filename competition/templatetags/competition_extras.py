from django import template

register = template.Library()


@register.filter(name='score_pretty')
def score_pretty(solution):
    return '?' if solution.score is None else solution.score

@register.filter
def batch(queryset, n=1):
    l = len(queryset)
    for ndx in range(0, l, n):
        yield queryset[ndx:min(ndx + n, l)]