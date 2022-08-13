"""Stubs for testing."""

from datetime import date
from typing import Any

from django.contrib.auth.models import User


class RequestStub:
    """Stub class for Django's request object in test cases."""

    # The stub object is not required to be a valid class.
    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        user: User = None,
        content_type: str = "application/json",
        authorization: str = "",
        query_params: dict[str, Any] = None,
    ):
        # pylint: disable=missing-function-docstring, invalid-name

        self.user = user
        self.content_type = content_type
        self.META = {"HTTP_AUTHORIZATION": authorization}
        self.query_params = query_params or {}


class UserStub:
    """Stub class for Django's user object in test cases."""

    # The stub object is not required to be a valid class.
    # pylint: disable=too-few-public-methods

    def __init__(self, username: str):
        # pylint: disable=missing-function-docstring

        self.username = username


class InitialStub:
    """Stub class for an abstract initial value in the replay service testing."""

    def __init__(self, value: int):
        # pylint: disable=missing-function-docstring

        self.value = value

    def __eq__(self, __o: object) -> bool:
        # pylint: disable=missing-function-docstring

        if not isinstance(__o, InitialStub):
            return NotImplemented

        return self.value == __o.value

    def __repr__(self) -> str:
        # pylint: disable=missing-function-docstring

        return f"""{self.value}"""


class DateBoundStub:
    """Stub class for an abstract action item value in the replay service testing."""

    # The stub object is not required to be a valid class.
    # pylint: disable=too-few-public-methods

    def __init__(self, value: int, date: date):
        # pylint: disable=missing-function-docstring, redefined-outer-name

        self.value = value
        self.date = date
