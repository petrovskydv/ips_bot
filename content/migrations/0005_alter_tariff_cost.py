# Generated by Django 3.2.4 on 2021-07-07 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_auto_20210707_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tariff',
            name='cost',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Стоимость'),
        ),
    ]