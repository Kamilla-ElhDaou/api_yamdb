from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import UserSerializer
from .permissions import IsAdmin

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Профиль текущего пользователя"""
    user = request.user
    serializer = UserSerializer(user)
    return render(request, 'users/profile.html', {'user': serializer.data})

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_me(request):
    """Получение и обновление профиля"""
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return render(request, 'users/me.html', {'user': serializer.data})
    
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return render(request, 'users/me.html', {'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdmin])
def user_list(request):
    """Список всех пользователей (только для админов)"""
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return render(request, 'users/list.html', {'users': serializer.data})

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdmin])
def user_detail(request, pk):
    """Детали пользователя (только для админов)"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return render(request, 'users/detail.html', {'user': serializer.data})
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return render(request, 'users/detail.html', {'user': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
