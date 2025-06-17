from datetime import datetime

from rest_framework import mixins, serializers, status, viewsets
from rest_framework.response import Response

from reviews.models import Title


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый вьюсет, предоставляет следующие действия:

    - create(создание)
    - list(получение списка)
    - destroy(удаление)
    Удобен для моделей, где не требуется обновление и детали.
    """


class NoPutRequestMixin:
    """Миксин для ограничения PUT-запросов."""

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': ' PUT-запрос не предусмотрен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class YearValidationMixin:
    """Миксин для валидации года."""

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
        """
        Создаёт объект Title с указанными
        данными и связывает его с жанрами.
        """
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        """
        Обновляет объект Title с новыми данными.

        и при необходимости обновляет связанные жанры.
        """
        genres = validated_data.pop('genre', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genres is not None:
            instance.genre.set(genres)
        return instance
