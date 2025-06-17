from rest_framework import serializers

from .mixins import TitleGenreSerializer, YearValidationMixin
from reviews.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    """
    Sеrializer для модели Category.
    """

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Sеrializer для модели Genre.
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Serializer для чтения Title.

    Возвращает вложенные жанры и категорию.
    """

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

class TitleWriteSerializer(
    TitleGenreSerializer, 
    YearValidationMixin,
    serializers.ModelSerializer
):
    """
    Serializer для создания и обновления Title.

    Использует SlugRelatedField для вложенных жанров и категории.
    """

    genre = serializers.SlugRelatedField(
        many=True, 
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        title = self.context['view'].get_title()
        user = self.context['request'].user
        if Review.objects.filter(title=title, author=user).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.'
            )
        return data

    def validate_score(self, data):
        if not 1 <= data <= 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')
        return data
