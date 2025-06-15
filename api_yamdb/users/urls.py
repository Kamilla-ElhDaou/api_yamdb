from django.urls import path
from .views import (
    user_me,
    user_list,
    user_detail,
    get_token,
    signup,
)


app_name = 'users'

urlpatterns = [
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/users/me/', user_me, name='user-me'),
    path('v1/users/', user_list, name='user-list'),
    path('v1/users/<str:username>/', user_detail, name='user-detail'),
]
