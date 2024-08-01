from rest_framework import serializers
from .models import Bank, ExchangeRate

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name', 'address', 'contact_number', 'website']

class ExchangeRateSerializer(serializers.ModelSerializer):
    bank = BankSerializer()  # To include bank details

    class Meta:
        model = ExchangeRate
        fields = ['id', 'bank', 'currency', 'buying_rate', 'selling_rate', 'transactional_buying_rate', 'transactional_selling_rate', 'date', 'updated_at']
