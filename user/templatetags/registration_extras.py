from django import template
from django.http import HttpRequest

register = template.Library()

@register.filter
def seminar(request: HttpRequest) -> str:
    return request.GET['seminar']
