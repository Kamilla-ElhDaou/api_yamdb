import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Система фильтрации для модели Title."""

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
