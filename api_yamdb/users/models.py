from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    bio = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=100, blank=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR
