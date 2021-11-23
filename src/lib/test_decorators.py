from django.test import SimpleTestCase

from .decorators import allow_content_types


class TestAllowContentTypes(SimpleTestCase):
    """
    Only allowing content type headers from the parameter iterable.
    """

    class RequestStub:
        def __init__(self, content_type):
            self.content_type = content_type

    def setUp(self):
        self.wrapped_view = allow_content_types(
            ('application/json', 'multipart/form-data'))(lambda x, y: x)

    def test_allowed_content_type(self):
        payload = {'test': 123}
        request = self.RequestStub('application/json')

        self.assertEqual(self.wrapped_view(payload, request), payload)

    def test_dissallowed_content_type(self):
        payload = {'test': 123}
        request = self.RequestStub('text/csv')

        result = self.wrapped_view(payload, request)

        self.assertNotEqual(result, payload)
        self.assertEqual(result.status_code, 400)