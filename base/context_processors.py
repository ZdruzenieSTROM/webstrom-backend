from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site


def sites(request):
    current_site = get_current_site(request)

    return {
        'current_site': current_site,
        'other_sites': Site.objects.exclude(pk=current_site.pk).order_by('pk'),
    }
