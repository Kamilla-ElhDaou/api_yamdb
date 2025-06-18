from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models


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

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
    )
    bio = models.TextField(blank=True, verbose_name='Биография',)
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
    )
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Код подтверждения',
    )

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
        message = f'Ваш код подтверждения: {self.confirmation_code}'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False
        )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
