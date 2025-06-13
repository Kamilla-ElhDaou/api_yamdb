from datetime import datetime

from rest_framework import serializers
from reviews.models import Title


class YearValidationMixin:

    def validate_year(self, value):
        """
        Проверка, что год не больше текущего
        """

        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего'
            )
        return value


class TitleGenreSerializer:
    """
    Специальный миксин для сериализатора Title.

    Обрабатывает жанры.
    """

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        genres = validated_data.pop('genre', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genres is not None:
            instance.genre.set(genres)
        return instance
