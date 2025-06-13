from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение которое позволяет изменять данные только администратору.

    Аутентифицированным пользователи с ролью is_admin  разрешены все действия.
    Остальные пользователи имеют доступ только для чтения.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )