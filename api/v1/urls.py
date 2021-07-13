from django.urls import path

from .views import (LoginApi, ChangeTariff, FetchCustomerInfo, fetch_tariffs_view, fetch_tariff,
                    fetch_available_tariffs_view, LogoutApi, add_tariff
)

urlpatterns = [
    path('login/', LoginApi.as_view()),
    path('logout/', LogoutApi.as_view()),
    path('customerinfo/', FetchCustomerInfo.as_view()),
    path('changetariff/', ChangeTariff.as_view()),
    path('tariffs/', fetch_tariffs_view),
    path('fetchavailabletarifs/', fetch_available_tariffs_view),
    path('tariffinfo/', fetch_tariff),
    path('addtariff/', add_tariff),
]
