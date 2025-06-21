from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrStaff
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignUpSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenSerializer,
                             UserSerializer)
from reviews.models import Category, Genre, Review, Title


User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaff,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

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


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaff,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

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
                               viewsets.GenericViewSet):
    """Базовый Вьюсет для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete']


class CategoryViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для работы с категориями произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для работы с жанрами произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с произведениями."""

    queryset = Title.objects.select_related(
        'category'
    ).prefetch_related(
        'genre'
    ).annotate(
        rating=Avg('reviews__score')
    )
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Возвращает нужный сериализатор в зависимости от метода."""
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class AuthViewSet(viewsets.ViewSet):
    """Вьюсет для работы с регистрацией и аутентификацией."""

    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """Регистрация пользователя и отправка кода подтверждения"""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        user.send_confirmation_email()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def token(self, request):
        """Получение токена по коду подтверждения."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Получить или изменить данные своей учетной записи"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data)
