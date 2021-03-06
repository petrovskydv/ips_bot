from django.urls import path

from .views import (
    LoginApi, ChangeTariff, FetchCustomerInfo, fetch_tariffs_view, fetch_tariff,
    fetch_available_tariffs_view, LogoutApi, add_tariff, make_promised_payment_view,
    check_promised_payment_view, fetch_payment_history_view, CheckDate, SetSuspend,
    suspension_settings, suspension_disable, check_authentication
)

urlpatterns = [
    path('login/', LoginApi.as_view()),
    path('logout/', LogoutApi.as_view()),
    path('suspension/set', SetSuspend.as_view()),
    path('suspension/settings', suspension_settings),
    path('suspension/disable', suspension_disable),
    path('customerinfo/', FetchCustomerInfo.as_view()),
    path('changetariff/', ChangeTariff.as_view()),
    path('tariffs/', fetch_tariffs_view),
    path('fetchavailabletarifs/', fetch_available_tariffs_view),
    path('tariffinfo/', fetch_tariff),
    path('addtariff/', add_tariff),
    path('promisedpayment/', make_promised_payment_view),
    path('promisedpayment/status', check_promised_payment_view),
    path('payments/history', fetch_payment_history_view),
    path('checkdate/', CheckDate.as_view()),
    path('check_authentication/', check_authentication),
]
