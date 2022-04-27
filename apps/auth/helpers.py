"""General helper functions for the auth module."""

from datetime import datetime, timedelta
from os import getenv
from typing import cast

import jwt
from django.contrib.auth.models import User


def generate_token(user: User, token_type: str = "access") -> str:  # nosec
    """Create a new JWT token encoding the provided information."""

    validity_interval = {
        "access": timedelta(days=1),
        "refresh": timedelta(days=30),
    }

    return jwt.encode(
        {
            "username": user.username,
            "type": token_type,
            "exp": datetime.now() + validity_interval[token_type],
        },
        algorithm="HS256",
        key=cast(str, getenv("JWT_SECRET")),
    )
