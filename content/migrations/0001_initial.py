# Generated by Django 3.2.4 on 2021-06-21 11:03

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=128, region=None, unique=True, verbose_name='Номер телефона')),
                ('email', models.CharField(blank=True, db_index=True, max_length=50, unique=True, verbose_name='Имеил')),
                ('login', models.CharField(blank=True, db_index=True, max_length=25, unique=True, verbose_name='Логин')),
                ('tg_chat_id', models.PositiveIntegerField(db_index=True, unique=True, verbose_name='Telegram chat ID')),
            ],
        ),
    ]
