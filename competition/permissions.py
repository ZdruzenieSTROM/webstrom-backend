from rest_framework import permissions


class CompetitionPermissionMixin:
    # pylint: disable=too-few-public-methods
    def can_user_modify(self, user):
        return len(set(self.permission_group.all()).intersection(set(user.groups.all()))) > 0


class ProblemPermission(permissions.BasePermission):
    """
    Prístup k objektom má iba staff
    """

    def has_permission(self, request, view):
        if view.action in ['retrieve']:
            return True

        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return obj.is_visible or (request.user.is_authenticated and request.user.is_staff)

        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_staff

        return False


class CompetitionRestrictedPermission(permissions.BasePermission):
    """
    Prístup k objektom má iba staff, výnimkou je retrieve viditeľných objektov
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.can_user_modify(request.user)
