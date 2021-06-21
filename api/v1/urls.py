from django.urls import path

from .views import RegestrationApi

urlpatterns = [
    path('credentials/', RegestrationApi.as_view()),
]
