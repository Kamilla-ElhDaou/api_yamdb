import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.mixins import NoPutRequestMixin
from users.models import User
from users.permissions import IsAdmin
from users.serializers import SignUpSerializer, TokenSerializer, UserSerializer


class AuthViewSet(viewsets.ViewSet):
    """Вьюсет для работы с регистрацией и аутентификацией."""

    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """Регистрация пользователя и отправка кода подтверждения"""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, created = User.objects.get_or_create(
            username=username,
            email=email,
            defaults={
                'confirmation_code': str(uuid.uuid4()),
                'is_active': False
            }
        )

        if not created:
            user.confirmation_code = str(uuid.uuid4())
            user.is_active = False
            user.save()

        user.send_confirmation_email()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def token(self, request):
        """Получение токена по коду подтверждения."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            return Response(
                {'confirmation_code': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = True
        user.save()

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(NoPutRequestMixin, viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

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
