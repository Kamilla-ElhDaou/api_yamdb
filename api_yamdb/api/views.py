from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.mixins import CreateListDestroyViewSet
from api.permissions import IsAdminOrReadOnly, IsAuthorOrStaff
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer
)
from reviews.models import Category, Genre, Review, Title


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

    queryset = Title.objects.all().select_related('category').prefetch_related('genre')
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
=======
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsAuthorOrStaff
from .serializers import ReviewSerializer, CommentSerializer
from reviews.models import Review, Title


class ReviewViewSet(viewsets.ModelViewSet):
    """API эндпоинт для работы с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaff]

    def get_title(self):
        """Получает произведение по id из URL или возвращает 404."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает queryset отзывов для конкретного произведения."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Создает новый отзыв с привязкой к произведению и автору."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """API эндпоинт для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaff]

    def get_review(self):
        """Получает отзыв по id и произведени из URL или возвращает 404."""
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        """Возвращает queryset комментариев для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Создает новый комментарий с привязкой к отзыву и автору."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
