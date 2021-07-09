from django.contrib import admin

from content.models import Tariff, Customer, Subscription

admin.site.register(Tariff)
admin.site.register(Customer)
admin.site.register(Subscription)