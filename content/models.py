from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    phonenumber = PhoneNumberField(
        "Номер телефона",
        db_index=True,
        unique=True,
        blank=True,
    )
    email = models.CharField(
        "Имеил",
        max_length=50,
        db_index=True,
        unique=True,
        blank=True,
    )
    login = models.CharField(
        "Логин",
        max_length=25,
        db_index=True,
        unique=True,
        blank=True,
    )
    tg_chat_id = models.PositiveIntegerField(
        'Telegram chat ID',
        db_index=True,
        unique=True
    )
