"""Test cases for the shared decorators."""

from django.test import SimpleTestCase

from .decorators import allow_content_types


class _RequestStub:
    """Stub class for Django's request object in test cases."""

    # The stub object is not required to be a valid class.
    # pylint: disable=too-few-public-methods

    def __init__(self, content_type):
        self.content_type = content_type


class TestAllowContentTypes(SimpleTestCase):
    """Only allowing content type headers from the parameter iterable."""

    def setUp(self):
        self.wrapped_view = allow_content_types(
            ("application/json", "multipart/form-data")
        )(lambda x, y: x)

    def test_allowed_content_type(self):
        payload = {"test": 123}
        request = _RequestStub("application/json")

        self.assertEqual(self.wrapped_view(payload, request), payload)

    def test_dissallowed_content_type(self):
        payload = {"test": 123}
        request = _RequestStub("text/csv")

        result = self.wrapped_view(payload, request)

        self.assertNotEqual(result, payload)
        self.assertEqual(result.status_code, 400)
