import uuid

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Tariff(models.Model):
    class Types(models.TextChoices):
        INTERNET = 'IN', ('Интернет')
        TV = 'TV', ('ТВ каналы')

    tariff_type = models.CharField(
        'Тип тарифа',
        max_length=2,
        choices=Types.choices,
        default=Types.INTERNET
    )
    netup_tariff_id = models.PositiveIntegerField(
        "Tariff ID",
        db_index=True,
        unique=True,
    )
    title = models.CharField(
        "Название тарифа",
        max_length=250
    )
    cost = models.PositiveIntegerField(
        "Стоимость",
        blank=True,
        null=True
    )
    description = models.TextField(
        "Описание тарифа",
        blank=True
    )
    instant_change = models.BooleanField(
        "Сразу ли сменится",
        blank=True,
        null=True
    )


class Customer(models.Model):
    # TODO придумать как красиво вернуть юник рестрикшен для альтернативных полей типов аутентификации
    phonenumber = PhoneNumberField(
        "Номер телефона",
        db_index=True,
        blank=True,
    )
    email = models.CharField(
        "Имеил",
        max_length=50,
        db_index=True,
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
        blank=True
    )
    tariffs = models.ManyToManyField(
        Tariff,
        through='Subscription',
        blank=True
    )
    netup_sid = models.TextField(
        "Айди сессии",
        blank=True
    )


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tariff_id = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name='Тариф')
    link_id = models.PositiveIntegerField()
