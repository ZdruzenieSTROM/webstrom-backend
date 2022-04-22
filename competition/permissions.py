from rest_framework import permissions


class CommentPermission(permissions.BasePermission):
    """
    Prístup k objektom má iba staff sutaze, výnimkou je retrieve publishnutých komentárov
    """

    def has_object_permission(self, request, view, obj):
        can_user_modify = obj.can_user_modify(request.user)

        if view.action == 'retrieve':
            if obj.published:
                return True
            if can_user_modify:
                return True
            if obj.posted_by == request.user:
                return True

        if view.action in ['publish', 'hide']:
            if can_user_modify:
                return True

        if view.action == 'edit':
            if obj.posted_by == request.user:
                return True

        if view.action == 'delete':
            if obj.posted_by == request.user or can_user_modify:
                return True

        return False


class CompetitionRestrictedPermission(permissions.BasePermission):
    """
    Prístup k objektom má iba staff, výnimkou je retrieve viditeľných objektov,
    osetrit vytvaranie objektov treba samostatne v danych views (?)
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.can_user_modify(request.user)
