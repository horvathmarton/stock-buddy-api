from collections.abc import Iterable

from rest_framework import status
from rest_framework.response import Response


def allow_content_types(supported_content_types: Iterable[str]) -> Response:
    """
    Decorate an endpoint function with it to only allow the content type header
    to be set to one of the values in the iterable.
    """

    def wrapper(func):
        def inner(*args, **kwargs):
            request = args[1]
            content_type = request.content_type.split(';')[0].strip()

            if content_type not in supported_content_types:
                return Response({
                    'error': f'Unsupported input format. ({content_type})'},
                    status=status.HTTP_400_BAD_REQUEST)

            return func(*args, **kwargs)

        return inner

    return wrapper
