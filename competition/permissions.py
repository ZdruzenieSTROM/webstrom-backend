from rest_framework import permissions

from .models import CommentPublishState, EventRegistration


class CommentPermission(permissions.BasePermission):
    """
    Prístup k objektom má iba staff sutaze, výnimkou je retrieve publishnutých komentárov
    """

    def has_object_permission(self, request, view, obj):
        can_user_modify = obj.can_user_modify(request.user)

        if view.action == 'retrieve':
            if obj.state == CommentPublishState.PUBLISHED\
                    or can_user_modify\
                    or obj.posted_by == request.user:
                return True

        if view.action in ['publish', 'hide']:
            if can_user_modify:
                return True

        if view.action == 'edit':
            # Vedúci vie vždy ediovať svoje komentáre
            # Účastník vie editovať iba svoje nezverejnené komentáre
            if (
                obj.posted_by == request.user
                and (
                    obj.state == CommentPublishState.WAITING_FOR_REVIEW
                    or can_user_modify
                )
            ):
                return True

        if view.action == 'destroy':
            # Vedúci vie mazať všetko
            # Používateľ vie zmazať iba svoj komentár
            if (
                obj.posted_by == request.user
                and obj.state == CommentPublishState.WAITING_FOR_REVIEW
            ) or can_user_modify:
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


class ProblemPermission(CompetitionRestrictedPermission):
    """Prístup pre Problem """

    def has_permission(self, request, view):
        if view.action in ['upload_solution', 'my_solution', 'corrected_solution', 'file_solution', 'file_corrected']:
            return request.user.is_authenticated

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action == 'upload_solution':
            return (
                request.user.is_authenticated and
                EventRegistration.get_registration_by_profile_and_event(
                    request.user.profile, obj.series.semester)
            ) and obj.series.can_submit

        if view.action in ['my_solution', 'corrected_solution']:
            return (
                request.user.is_authenticated and
                EventRegistration.get_registration_by_profile_and_event(
                    request.user.profile, obj.series.semester))

        if view.action in ['file_solution', 'file_corrected', 'upload_solution_file', 'upload_corrected_solution_file']:
            return request.user.is_authenticated and obj.can_user_modify(request.user)

        return super().has_object_permission(request, view, obj)
