from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


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

    def validate_score(self, data):
        """Проверяет корректность введенной оценки."""
        if not 1 <= data <= 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')
        return data


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели произведений."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category',)
        read_only_fields = fields

    def get_rating(self, obj):
        """Вычисляет средний рейтинг на основе отзывов."""
        return obj.reviews.aggregate(Avg('score'))['score__avg']


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для для создания и обновления модели произведений."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        required=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        required=True,
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def validate_genre(self, data):
        """Проверяет корректность введенного жанра."""
        if not data:
            raise serializers.ValidationError({
                'genre': 'Жанр необходимо указать'
            })
        return data

    def validate_category(self, data):
        """Проверяет корректность введенной категории."""
        if not data:
            raise serializers.ValidationError({
                'category': 'Категорию необходимо указать'
            })
        return data

    def validate_year(self, value):
        """Проверяет, что год выпуска не превышает текущий."""
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего'
            )
        return value

    def create(self, validated_data):
        """Создает новое произведение."""
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        """Обновляет произведение."""
        genres = validated_data.pop('genre', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genres is not None:
            instance.genre.set(genres)
        return instance

    def to_representation(self, instance):
        """Переключение на сериализатор для чтения для ответа."""
        return TitleReadSerializer(instance).data
