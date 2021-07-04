from django.urls import path

from .views import RegistrationApi

urlpatterns = [
    path('credentials/', RegistrationApi.as_view()),
]
