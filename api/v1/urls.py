from django.urls import path

from .views import (RegistrationApi, LoginApi, ChangeTariff, FetchCustomerInfo, fetch_tariffs_view, fetch_tariff,
                    fetch_available_tariffs_view, LogoutApi
)

urlpatterns = [
    path('credentials/', RegistrationApi.as_view()),
    path('login/', LoginApi.as_view()),
    path('logout/', LogoutApi.as_view()),
    path('customerinfo/', FetchCustomerInfo.as_view()),
    path('changetariff/', ChangeTariff.as_view()),
    path('tariffs/', fetch_tariffs_view),
    path('fetchavailabletarifs/', fetch_available_tariffs_view),
    path('tariffinfo/', fetch_tariff),
]
