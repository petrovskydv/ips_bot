# Generated by Django 3.2.4 on 2021-07-09 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_alter_tariff_instant_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='netup_account_id',
            field=models.CharField(blank=True, max_length=30, verbose_name='Биллинг айди'),
        ),
    ]
