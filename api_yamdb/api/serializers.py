from rest_framework import serializers

from reviews.models import Category, Genre, Title
from .mixins import TitleGenreSerializer, YearValidationMixin


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
