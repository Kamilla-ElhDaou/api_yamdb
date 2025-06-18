from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrStaff(BasePermission):
    """Проверяет является ли пользователь автором или администратором."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """Проверяет является ли пользователь администратором."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )
