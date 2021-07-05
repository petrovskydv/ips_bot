from django.urls import path

from .views import RegistrationApi, LoginApi, ChangeTariff

urlpatterns = [
    path('credentials/', RegistrationApi.as_view()),
    path('login/', LoginApi.as_view()),
    path('changetariff/', ChangeTariff.as_view()),
    path('tariffs/', ChangeTariff.as_view()),
]
