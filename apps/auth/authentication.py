"""Authentication related config items for Django."""

from os import getenv
from typing import cast

import jwt
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class JwtAuthentication(BaseAuthentication):
    """Custom authentication class for the JWT token auth."""

    def authenticate(self, request: Request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) == 1 or len(auth) > 2:
            raise AuthenticationFailed(
                "Please provide a valid bearer token in the authorization header."
            )

        try:
            token = jwt.decode(
                auth[1].decode(),
                algorithms=["HS256"],
                key=cast(str, getenv("JWT_SECRET")),
            )
        except jwt.ExpiredSignatureError as error:
            raise AuthenticationFailed("The token has been expired.") from error
        except jwt.InvalidSignatureError as error:
            raise AuthenticationFailed("The token signature is invalid.") from error
        except Exception as error:
            raise AuthenticationFailed() from error

        try:
            user = User.objects.get(username=token["username"])
        except User.DoesNotExist as error:
            raise AuthenticationFailed("User doesn't exist.") from error

        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"
