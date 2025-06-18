from rest_framework import serializers

from users.constants import FORBIDDEN_NAMES


class UsernameValidationMixin:
    def validate_username(self, data):
        """Проверяте, что имя пользователя не запрещенно."""
        if data.lower() in FORBIDDEN_NAMES:
            raise serializers.ValidationError(
                f'Имя пользователя не может быть {data}'
            )
        return data
