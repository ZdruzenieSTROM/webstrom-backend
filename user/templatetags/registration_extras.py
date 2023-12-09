from django import template
from django.http import HttpRequest

register = template.Library()


@register.filter
def seminar(request: HttpRequest) -> str:
    return request.GET['seminar']


@register.filter
def source_host(request: HttpRequest) -> str:
    return request.META.get('HTTP_X_FORWARDED_HOST', 'localhost:3000')
