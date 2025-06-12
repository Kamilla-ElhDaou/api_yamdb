from api.mixins import CreateListDestroyViewSet
from api.permissions import IsAdminOrReadOnly
from api.serializers import (CategorySerializer, GenreSerializer,
                             TitleCreateUpdateSerializer, TitleSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
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
    filter_backends = (filters.SearchFilter)
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
    filter_backends = (filters.SearchFilter)
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
        Возвращает соответствующий сериализатор: 
        - list и retrieve: сериализатор для чтения (вложенные жанры и категории)
        - остальные операции: сериализатор для записи по слагу.
        """
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleCreateUpdateSerializer
