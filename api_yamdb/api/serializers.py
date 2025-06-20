from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from constants import (MAX_EMAIL_LENGTH, MAX_FIRST_NAME_LENGTH,
                       MAX_LAST_NAME_LENGTH, MAX_USERNAME_LENGTH,)
from api.mixins import UsernameValidationMixin
from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с комментариями к отзывам."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с отзывами к произведениям."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        """Проверяет, чтобы был единственный отзыв."""
        if self.context['request'].method != 'POST':
            return data

        title = self.context['view'].get_title()
        user = self.context['request'].user
        if Review.objects.filter(title=title, author=user).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категриями произведений."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о произведении."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, allow_null=True,)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category',)
        read_only_fields = fields


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления произведений."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        required=True,
        allow_empty=False,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        required=True,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        """Переключение на сериализатор для чтения для ответа."""
        return TitleReadSerializer(instance).data


class UserSerializer(UsernameValidationMixin, serializers.ModelSerializer):
    """Сериализатор для работы с данными пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'username': {
                'max_length': MAX_USERNAME_LENGTH
            },
            'email': {
                'max_length': MAX_EMAIL_LENGTH
            },
            'first_name': {
                'max_length': MAX_FIRST_NAME_LENGTH
            },
            'last_name': {
                'max_length': MAX_LAST_NAME_LENGTH
            }
        }

    def validate(self, data):
        """Проверка данных при PATCH запросе."""
        if self.instance:

            username = data.get('username')
            email = data.get('email')

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

        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Проверяет корректность кода подтверждения."""
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
            user, data['confirmation_code']
        ):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )
        data['user'] = user
        return data


class SignUpSerializer(UsernameValidationMixin, serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(required=True, max_length=MAX_EMAIL_LENGTH)
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH,
        validators=[User.username_validator]
    )

    def validate(self, data):
        """Проверка доступности имени пользователя и электронной почты."""
        username = data.get('username')
        email = data.get('email')

        user_exists = User.objects.filter(
            username=username,
            email=email
        ).exists()

        if user_exists:
            return data

        username_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        if username_exists or email_exists:
            errors = {}
            if username_exists:
                errors['username'] = 'Пользователь с таким именем существует'
            if email_exists:
                errors['email'] = 'Пользователь с таким email существует'
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        """Создает пользователя или возвращает существующего."""
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
            defaults={
                'is_active': False
            }
        )

        if not created:
            user.save()
        return user
