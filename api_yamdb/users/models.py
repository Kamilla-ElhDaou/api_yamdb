from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models

from constants import FORBIDDEN_NAMES, MAX_USERNAME_LENGTH


def validate_username(data):
    if data in FORBIDDEN_NAMES:
        raise ValidationError(
            f'Имя пользователя не может быть {data}'
        )


class User(AbstractUser):
    """
    Модель для пользователя.

    Атрибуты:
        role (CharField): Роль пользователя.
        bio (TextField): Биография.
        email (EmailField): Электронная почта.
        confirmation_code (CharField): Код подтверждения.

    Свойства:
        is_admin (bool): Возвращает True если пользователь имеет роль
            администратора или является суперпользователем.
        is_moderator (bool): Возвращает True если пользователь
            имеет роль модератора.

    Методы:
        send_confirmation_email(): Отправляет email с кодом подтверждения
            на адрес пользователя.
    """

    class Role(models.TextChoices):
        """Варианты ролей пользователей."""

        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[AbstractUser.username_validator, validate_username],
        verbose_name='Имя пользователя',
    )
    role = models.CharField(
        max_length=max(len(role) for role in Role.values),
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
    )
    bio = models.TextField(blank=True, verbose_name='Биография',)
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == self.Role.MODERATOR

    def send_confirmation_email(self):
        """
        Генерирует письмо с кодом подтверждения и отправляет его
        на email пользователя.
        """
        subject = 'Код подтверждения для YaMDb'
        confirmation_code = default_token_generator.make_token(self)
        message = f'Ваш код подтверждения: {confirmation_code}'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False
        )
