from rest_framework import serializers

from constants import FORBIDDEN_NAMES


class UsernameValidationMixin:
    """Проверяет, что имя пользователя не запрещенно."""

    def validate_username(self, data):
        if data in FORBIDDEN_NAMES:
            raise serializers.ValidationError(
                f'Имя пользователя не может быть {data}'
            )
        return data
