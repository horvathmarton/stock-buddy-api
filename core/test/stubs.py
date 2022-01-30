"""Stubs for testing."""

from django.contrib.auth.models import User


class RequestStub:
    """Stub class for Django's request object in test cases."""

    # The stub object is not required to be a valid class.
    # pylint: disable=too-few-public-methods

    def __init__(self, user: User = None, content_type: str = "application/json"):
        self.user = user
        self.content_type = content_type
