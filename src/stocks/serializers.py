from rest_framework import serializers

from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(max_length=8)
    name = serializers.TextField()

    class Meta:
        model = Stock
        fields = ('__all__')