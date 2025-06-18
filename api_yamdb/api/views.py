from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly

from api.mixins import NoPutRequestMixin, TitleFilter
from api.permissions import IsAdminOrReadOnly, IsAuthorOrStaff
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleReadSerializer, TitleWriteSerializer)
from reviews.models import Category, Genre, Review, Title


class ReviewViewSet(NoPutRequestMixin, viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaff,)
    pagination_class = LimitOffsetPagination

    def get_title(self):
        """Получает произведение по id из URL или возвращает 404."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает queryset отзывов для конкретного произведения."""
        title = self.get_title()
        return title.reviews.select_related('author').all()

    def perform_create(self, serializer):
        """Создает новый отзыв с привязкой к произведению и автору."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(NoPutRequestMixin, viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaff,)
    pagination_class = LimitOffsetPagination

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
        return review.comments.select_related('author').all()

    def perform_create(self, serializer):
        """Создает новый комментарий с привязкой к отзыву и автору."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


class CategoryGenreBaseViewSet(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet,
                               NoPutRequestMixin):
    """Базовый Вьюсет для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination


class CategoryViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для работы с категориями произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для работы с жанрами произведений."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(NoPutRequestMixin, viewsets.ModelViewSet):
    """Вьюсет для работы с произведениями."""

    queryset = Title.objects.select_related(
        'category').prefetch_related('genre')
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_class = TitleFilter
    ordering_fields = ('name', 'year',)
    search_fields = ('name', 'genre__name',)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        """Возвращает нужный сериализатор в зависимости от метода."""

        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer
