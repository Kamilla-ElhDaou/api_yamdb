from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from api.mixins import CreateListDestroyViewSet
from api.permissions import IsAdminOrReadOnly
from api.serializers import (
    CategorySerializer, 
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer
)
from reviews.models import Category, Genre, Title


class CategoryViewSet(CreateListDestroyViewSet):
    """
    Вьюсет категорий произведений.

    Позволяет админам создавать, удалять и просматривать категории.
    Остальным пользователям доступен только просмотр.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('name', 'slug')
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """
    Вьюсет жанров произведений.

    Поведение аналогично CategoryViewSet
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет произведений.

    Полный CRUD с разными сериализаторами
    для чтения и записи. Доступ: поиск, фильтрация, сортировка
    """

    queryset = Title.objects.all()
    filter_backends = [
        DjangoFilterBackend, 
        filters.OrderingFilter, 
        filters.SearchFilter
    ]
    filterset_fields = ['category', 'genre', 'year']
    ordering_fields = ['name', 'year']
    search_fields = ['name']

    def get_serializer_class(self):
        """
        Возвращает сериализатор для операций чтения (list, retrieve)
        или для создания/обновления
        """

        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer
