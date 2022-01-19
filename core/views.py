"""Business logic for the raw data module."""

from typing import Any
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class RootView(APIView):
    """A simple root view that is accessible for everyone."""

    permission_classes: list[Any] = []

    def get(self, request: Request) -> Response:
        """Health check function for the application."""

        return Response({"status": "ok"})
