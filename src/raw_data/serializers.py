from rest_framework import serializers

from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(max_length=16)
    name = serializers.CharField()

    class Meta:
        model = Stock
        fields = ('__all__')
