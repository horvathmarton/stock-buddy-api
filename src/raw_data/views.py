from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Stock
from .serializers import StockSerializer

class StockViews(APIView):
    def get(self, request, id=None):
        pass

    
    def post(self, request):
        pass


    def patch(self, request, id=None):
        pass


    def delete(self, request, id=None):
        pass