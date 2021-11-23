from rest_framework import serializers

from .models import Stock, StockPortfolio, StockWatchlist


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = ('ticker', 'name', 'description', 'sector')


class StockPortfolioSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = StockPortfolio
        fields = ('name', 'description', 'owner')


class StockWatchlistSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = StockWatchlist
        fields = ('name', 'description', 'owner')
