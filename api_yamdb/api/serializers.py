from rest_framework import serializers
from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """
    Сеrializer для модели Category.

    Поля:
        name - название категории
        slug - уникальный слаг категории
    """

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Сеrializer для модели Genre.

    Поля:
        name - название жанра
        slug - уникальный слаг жанра
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """
    Сеrializer для модели Title.

    Поля:
        genre - вложенный сеrializer Genre(many=True, read_only=True)
        category - вложенный сеrializer Category
        остальные поля модели Title
    """

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer для создания и обновления модели Title.

    Поля:
        genre: Список слагов жанров (SlugRelatedField).
        category: Слаг категории (SlugRelatedField).
        остальные поля модели Title.
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
