import django_filters
from rest_framework.response import Response
from rest_framework import status

from reviews.models import Title


class NoPutRequestMixin:
    """Миксин для ограничения PUT-запросов."""

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': ' PUT-запрос не предусмотрен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class TitleFilter(django_filters.FilterSet):
    """Система фильтрации для модели Title"""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']
