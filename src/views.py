"""Business logic for the raw data module."""

from os import path

from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from .version import __VERSION__


try:
    with open(
        path.join(path.dirname(__file__), "../current_commit.txt"), encoding="utf-8"
    ) as f:
        CURRENT_COMMIT = f.read().splitlines()[0]
except FileNotFoundError:
    CURRENT_COMMIT = "unknown"


@api_view(["GET"])
@permission_classes([])
def root_handler(request: Request) -> Response:
    """Health check function for the application."""

    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([])
def version_handler(request: Request) -> Response:
    """Return version and commmit hash information."""

    return Response({"version": __VERSION__, "commit": CURRENT_COMMIT})
