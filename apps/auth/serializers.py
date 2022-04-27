"""Serializers for the auth payloads."""

from rest_framework.serializers import Serializer, CharField


class SignInSerializer(Serializer):
    """Serializer of the sign-in payload."""

    # pylint: disable=abstract-method

    username = CharField(max_length=150)
    password = CharField(max_length=150)


class RefreshTokenSerializer(Serializer):
    """Serializer of the token refresh payload."""

    # pylint: disable=abstract-method

    token = CharField(max_length=150)


class ChangePasswordSerializer(Serializer):
    """Serializer of the password change payload."""

    # pylint: disable=abstract-method

    password = CharField(max_length=150)
