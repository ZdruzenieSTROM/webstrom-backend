import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django_sendfile import sendfile
from rest_framework.request import Request


@login_required
def download_protected_file(request: Request, model_class, path_prefix, path):
    """
    This view allows download of the file at the specified path, if the user
    is allowed to. This is checked by calling the model's can_access_files
    method.
    """
    filepath = os.path.join(settings.PRIVATE_STORAGE_ROOT, path_prefix, path)
    filepath_mediapath = path_prefix + path

    if request.user.is_authenticated:
        # Superusers can access all files
        if request.user.is_superuser:
            return sendfile(request, filepath)
        obj = model_class.get_by_filepath(filepath_mediapath)

        if obj is not None and obj.can_access(request.user):
            return sendfile(request, filepath)

    raise PermissionDenied
