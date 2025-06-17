import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.conf import settings


class User(AbstractUser):
    """Кастомная модель пользователя с расширенными полями."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
    )
    confirmation_code = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Строковое представление пользователя."""
        return f'{self.username} ({self.email})'

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == self.MODERATOR

    def send_confirmation_email(self):
        """Отправляет email с кодом подтверждения."""
        self.confirmation_code = str(uuid.uuid4())
        self.save()
        send_mail(
            'YaMDb: Подтверждение регистрации',
            f'Ваш код подтверждения: {self.confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
