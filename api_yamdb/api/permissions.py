from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrStaff(BasePermission):
    """
    Разрешает доступ к объекту если:
    - Запрос безопасный - всем.
    - Пользователь является автором объекта.
    - Пользователь имеет права модератора или администратора.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ на чтение всем пользователям,
    а изменение данных аутентифицированным администраторам.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdmin(BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request, view):
        return request.user.is_admin
