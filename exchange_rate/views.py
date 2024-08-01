from rest_framework import generics
from .models import Bank, ExchangeRate
from .serializers import BankSerializer, ExchangeRateSerializer

class BankListView(generics.ListCreateAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class BankDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class ExchangeRateListView(generics.ListCreateAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer

class ExchangeRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
