from django.contrib import admin

from content.models import Tariff, Customer, Subscription

admin.site.register(Subscription)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = [
        'login',
    ]
    list_display = [
        'login',
        'tg_chat_id',
    ]
    ordering = ['login']


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    search_fields = [
        'title',
    ]
    list_display = [
        'title',
        'tariff_type',
        'cost',
    ]
    ordering = ['title']
