"""Define the URL schemes for the auth route."""

from django.urls import path

from .views import change_password_handler, refresh_token_handler, sing_in_handler

urlpatterns = [
    path("sign-in", sing_in_handler),
    path("refresh-token", refresh_token_handler),
    path("change-password", change_password_handler),
]
