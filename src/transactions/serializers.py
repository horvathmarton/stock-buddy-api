from rest_framework import serializers

from .models import CashTransaction, ForexTransaction, StockTransaction


class CashTransactionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = CashTransaction
        fields = ('currency', 'amount', 'date', 'owner', 'portfolio')


class ForexTransactionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = ForexTransaction
        fields = ('date', 'amount', 'ratio', 'source_currency',
                  'target_currency', 'owner', 'portfolio')


class StockTransactionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = StockTransaction
        fields = ('ticker', 'amount', 'price', 'date',
                  'comment', 'owner', 'portfolio')
