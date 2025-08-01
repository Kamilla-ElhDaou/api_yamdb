from django.urls import include, path
from rest_framework import routers

from api.views import (AuthViewSet, CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet, UserViewSet)


app_name = 'api'

v1_router = routers.DefaultRouter()

v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('auth', AuthViewSet, basename='auth')

v1_api_urlpatterns = [
    path('', include(v1_router.urls)),
]

urlpatterns = [
    path('v1/', include(v1_api_urlpatterns)),
]
