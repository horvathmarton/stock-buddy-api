from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class RootView(APIView):
    permission_classes = []

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})
