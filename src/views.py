"""Business logic for the raw data module."""

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def root_handler(request: Request) -> Response:
    """Health check function for the application."""

    return Response({"status": "ok"})
