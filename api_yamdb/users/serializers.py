from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.mixins import UsernameValidationMixin


User = get_user_model()


class UserSerializer(UsernameValidationMixin, serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'username': {
                'max_length': 150
            },
            'email': {
                'max_length': 254
            },
            'first_name': {
                'max_length': 150
            },
            'last_name': {
                'max_length': 150
            }
        }

    def validate(self, data):
        """Проверка данных при PATCH запросе."""
        if self.instance:

            username = data.get('username')
            email = data.get('email')
            # first_name = data.get('first_name')
            # last_name = data.get('last_name')

            if email and email != self.instance.email:
                if User.objects.filter(email=email).exists():
                    raise serializers.ValidationError(
                        {'email': 'Адрес электронной почты занят'}
                    )
            if username and username != self.instance.username:
                if User.objects.filter(username=data['username']).exists():
                    raise serializers.ValidationError(
                        {'username': 'Имя пользователя занято'}
                    )

            # if email and email != self.instance.email:
            #     if len(email) > 254:
            #         raise serializers.ValidationError(
            #             {'email': 'Слишком длинный адрес электронной почты'}
            #         )
            #     if User.objects.filter(email=email).exists():
            #         raise serializers.ValidationError(
            #             {'email': 'Адрес электронной почты занят'}
            #         )
            # if username and username != self.instance.username:
            #     if len(username) > 150:
            #         raise serializers.ValidationError(
            #             {'username': 'Слишком длинное имя пользователя'}
            #         )
            #     if User.objects.filter(username=data['username']).exists():
            #         raise serializers.ValidationError(
            #             {'username': 'Имя пользователя занято'}
            #         )
            # if first_name and len(first_name) > 150:
            #     raise serializers.ValidationError(
            #         {'first_name': 'Слишком длинное имя'}
            #     )
            # if last_name and len(last_name) > 150:
            #     raise serializers.ValidationError(
            #         {'last_name': 'Слишком длинная фамилия'}
            #     )
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class SignUpSerializer(UsernameValidationMixin, serializers.Serializer):
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

        if username_exists and email_exists:
            user_1 = User.objects.get(username=username)
            user_2 = User.objects.get(email=email)
            if user_1 != user_2:
                raise serializers.ValidationError(
                    {'username': 'Пользователь с таким именем уже существует',
                     'email': 'Пользователь с таким email уже существует'}
                )

        if username_exists:
            existing_user = User.objects.get(username=username)
            if existing_user.email != email:
                raise serializers.ValidationError(
                    {'username': 'Пользователь с таким именем уже существует'}
                )

        if email_exists:
            existing_user = User.objects.get(email=email)
            if existing_user.username != username:
                raise serializers.ValidationError(
                    {'email': 'Пользователь с таким email уже существует'}
                )

        return data
