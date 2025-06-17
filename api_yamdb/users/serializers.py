from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[User.username_validator]
    )

    def validate(self, data):
        """Проверка доступности имени пользователя и электронной почты."""
        username = data.get('username')
        email = data.get('email')

        username_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        if username_exists:
            existing_user = User.objects.get(username=username)
            if existing_user.email != email:
                raise serializers.ValidationError(
                    {'email': 'Пользователь с таким именем уже существует'}
                )

        if email_exists:
            existing_user = User.objects.get(email=email)
            if existing_user.username != username:
                raise serializers.ValidationError(
                    {'username': 'Пользователь с таким email уже существует'}
                )

        return data

    def validate_username(self, data):
        """Проверяте, что имя пользователя не является 'me'"""
        if data.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me"'
            )
        return data
