from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CashTransaction


class CashTransactionsView(APIView):
    def get(self, request, format=None):
        cash_transactions = CashTransaction.objects.all()

        return Response(cash_transactions)

    def post(self, request, format=None):
        tx = CashTransaction(
            currency='HUF', amount=request.data['amount'], date=request.data['date'], user=1)
        tx.save()

        return Response(None, status=status.HTTP_201_CREATED)
