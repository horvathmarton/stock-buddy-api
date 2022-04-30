"""Test cases for the shared decorators."""

from django.test import SimpleTestCase
from src.lib.decorators import allow_content_types

from ..stubs import RequestStub


class TestAllowContentTypes(SimpleTestCase):
    """Only allowing content type headers from the parameter iterable."""

    def setUp(self):
        self.wrapped_view = allow_content_types(
            ("application/json", "multipart/form-data")
        )(lambda x, y: x)

    def test_allowed_content_type(self):
        payload = {"test": 123}
        request = RequestStub(content_type="application/json")

        self.assertEqual(self.wrapped_view(payload, request), payload)

    def test_dissallowed_content_type(self):
        payload = {"test": 123}
        request = RequestStub(content_type="text/csv")

        result = self.wrapped_view(payload, request)

        self.assertNotEqual(result, payload)
        self.assertEqual(result.status_code, 400)
