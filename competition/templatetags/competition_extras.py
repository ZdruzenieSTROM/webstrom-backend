from django import template

register = template.Library()

@register.filter(name='score_pretty')
def score_pretty(solution):
    return '?' if not solution.score else solution.score
