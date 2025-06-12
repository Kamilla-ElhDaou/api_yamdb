from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SignUpAPIView, TokenAPIView

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('auth/signup/', SignUpAPIView.as_view()),
    path('auth/token/', TokenAPIView.as_view()),
] + router.urls
