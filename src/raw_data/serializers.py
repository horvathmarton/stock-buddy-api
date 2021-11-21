from dateutil import parser
from django.db.models import Max
from rest_framework import serializers

from .models import StockPrice, StockDividend, StockSplit


class StockPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockPrice
        fields = ['date', 'value']


class StockDividendSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockDividend
        fields = ['declaration_date',
                  'ex_dividend_date', 'payout_date', 'amount']


class StockSplitSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockSplit
        fields = ['date', 'ratio']
