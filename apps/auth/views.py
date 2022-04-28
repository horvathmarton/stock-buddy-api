"""Business logic for the auth module."""

from os import getenv
from typing import cast

import jwt
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import (
    ChangePasswordSerializer,
    RefreshTokenSerializer,
    SignInSerializer,
)
from .helpers import generate_token


@api_view(["POST"])
@permission_classes([])
def sing_in_handler(request: Request) -> Response:
    """Checks the user credentials and generates a JWT token pair."""

    serializer = SignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(username=serializer.validated_data["username"])
    except User.DoesNotExist as error:
        raise AuthenticationFailed("Invalid username or password.") from error

    if not user.check_password(serializer.validated_data["password"]):
        raise AuthenticationFailed("Invalid username or password.")

    user.last_login = timezone.now()
    user.save()

    return Response(
        {
            "access": generate_token(user),
            "refresh": generate_token(user, token_type="refresh"),  # nosec
        }
    )


@api_view(["POST"])
def refresh_token_handler(request: Request) -> Response:
    """Validates the refresh token of the user and generates a new JWT token pair."""

    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        refresh_token = jwt.decode(
            serializer.validated_data["token"],
            algorithms=["HS256"],
            key=cast(str, getenv("JWT_SECRET")),
        )
    except jwt.ExpiredSignatureError as error:
        raise AuthenticationFailed("The token has been expired.") from error
    except jwt.InvalidSignatureError as error:
        raise AuthenticationFailed("The token signature is invalid.") from error
    except Exception as error:
        raise AuthenticationFailed() from error

    user = cast(User, request.user)

    if user.username != refresh_token["username"]:
        raise AuthenticationFailed()

    tokens = {
        "access": generate_token(user),
        "refresh": generate_token(user, token_type="refresh"),  # nosec
    }

    return Response(tokens)


@api_view(["POST"])
def change_password_handler(request: Request) -> Response:
    """Updates the authenticated user's password."""

    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = cast(User, request.user)

    user.set_password(serializer.validated_data["password"])
    user.save()

    return Response(status=204)
