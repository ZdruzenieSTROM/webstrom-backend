from rest_framework import permissions


class PostPermission(permissions.BasePermission):
    """
    Prístup k objektom má iba staff, výnimkou je retrieve viditeľných objektov
    """

    def has_permission(self, request, view):
        if view.action in ['visible', 'retrieve']:
            return True

        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return obj.is_visible or (request.user.is_authenticated and request.user.is_staff)

        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_staff

        return False
