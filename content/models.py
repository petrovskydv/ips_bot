import uuid

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Tariff(models.Model):
    netup_tariff_id = models.PositiveIntegerField(
        "Tariff ID",
        db_index=True,
        unique=True,
    )
    title = models.CharField(
        "Название тарифа",
        max_length=250
    )
    netup_tariff_link_id = models.PositiveIntegerField(
        "Tariff link ID",
        db_index=True,
        unique=True,
    )
    cost = models.PositiveIntegerField(
        "Стоимость",
    )
    main = models.BooleanField(
        "Основной тариф"
    )


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
    password = models.CharField(
        "Пароль",
        max_length=100,
        blank=True,
    )
    tg_chat_id = models.PositiveIntegerField(
        "Telegram chat ID",
        db_index=True,
        unique=True,
    )
    netup_account_id = models.CharField(
        "Биллинг айди",
        max_length=30,
        blank=True,
        unique=True
    )
    tariffs = models.ManyToManyField(
        Tariff,
        through='TariffRelation',
        blank=True
    )


class TariffRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    tariff_id = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name='Тариф')
