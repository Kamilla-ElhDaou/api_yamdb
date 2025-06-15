from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer,
    UserMeSerializer,
    SignUpSerializer,
    TokenSerializer
)
from .permissions import IsAdmin, IsAdminOrReadOnly


User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """Вьюсет для аутентификации."""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def signup(self, request):
        """Регистрация нового пользователя."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user, created = User.objects.get_or_create(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username']
        )
        
        confirmation_code = str(uuid.uuid4())
        user.confirmation_code = confirmation_code
        user.save()
        
        send_mail(
            'YaMDb: Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            'yamdb@example.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def token(self, request):
        """Получение JWT-токена."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'],
            confirmation_code=serializer.validated_data['confirmation_code']
        )
        
        refresh = RefreshToken.for_user(user)
        return Response({'token': str(refresh.access_token)})


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    
    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        serializer_class=UserMeSerializer
    )
    def me(self, request):
        """Получение и редактирование своего профиля."""
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
        serializer.save()
        return Response(serializer.data)
