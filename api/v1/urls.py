from django.urls import path

from .views import (
    LoginApi, ChangeTariff, FetchCustomerInfo, fetch_tariffs_view, fetch_tariff,
    fetch_available_tariffs_view, LogoutApi, add_tariff, make_promised_payment_view,
    check_promised_payment_view, fetch_payment_history_view, CheckDate, SetSuspend,
    suspention_settings
)

urlpatterns = [
    path('login/', LoginApi.as_view()),
    path('logout/', LogoutApi.as_view()),
    path('suspention/set', SetSuspend.as_view()),
    path('suspention/settings', suspention_settings),
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
]
