from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        'Почта',
        unique=True,
        blank=False,
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        blank=False,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=False,
    )
    is_subscribed = models.BooleanField(
        default=False
    )
