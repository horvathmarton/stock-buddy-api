"""Decorators shared throughout the project."""

from collections.abc import Iterable
from logging import getLogger
from typing import Any, Callable

from rest_framework import status
from rest_framework.response import Response

LOGGER = getLogger(__name__)


def allow_content_types(
    supported_content_types: Iterable[str],
) -> Callable[[Any], Any]:
    """
    Decorate an endpoint function with it to only allow the content type header
    to be set to one of the values in the iterable.
    """

    def wrapper(func):
        def inner(*args, **kwargs):
            LOGGER.debug("Parsing the Content-Type header from the request.")
            request = args[1]
            content_type = request.content_type.split(";")[0].strip()

            LOGGER.debug("Validating if the content type is supported.")
            if content_type not in supported_content_types:
                return Response(
                    {"error": f"Unsupported input format. ({content_type})"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return func(*args, **kwargs)

        return inner

    return wrapper
