from django.urls import re_path

from competition.models import Solution

from .views import download_protected_file

urlpatterns = [
    # Include non-translated versions only since Admin ignores lang prefix
    re_path(r'solutions/(?P<path>.*)$', download_protected_file,
            {'path_prefix': 'solutions/', 'model_class': Solution},
            name='download_solution'),
    re_path(r'corrected_solutions/(?P<path>.*)$', download_protected_file,
            {'path_prefix': 'corrected_solutions/',
             'model_class': Solution},
            name='download_corrected_solution'),
]
