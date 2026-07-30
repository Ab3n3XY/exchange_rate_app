from rest_framework import serializers
from .models import Bank, ExchangeRate, Fuel

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name', 'address', 'contact_number', 'website']

class ExchangeRateSerializer(serializers.ModelSerializer):
    bank = BankSerializer()  # To include bank details
    buying_rate_difference = serializers.SerializerMethodField()
    selling_rate_difference = serializers.SerializerMethodField()
    transactional_buying_rate_difference = serializers.SerializerMethodField()
    transactional_selling_rate_difference = serializers.SerializerMethodField()

    class Meta:
        model = ExchangeRate
        fields = ['id', 'bank', 'currency', 'buying_rate', 'selling_rate', 
                  'transactional_buying_rate', 'transactional_selling_rate', 
                  'date', 'updated_at', 'buying_rate_difference', 
                  'selling_rate_difference', 'transactional_buying_rate_difference', 
                  'transactional_selling_rate_difference']

    def get_buying_rate_difference(self, obj):
        return obj.buying_rate_difference

    def get_selling_rate_difference(self, obj):
        return obj.selling_rate_difference

    def get_transactional_buying_rate_difference(self, obj):
        return obj.transactional_buying_rate_difference

    def get_transactional_selling_rate_difference(self, obj):
        return obj.transactional_selling_rate_difference

class ExchangeChartRateSerializer(serializers.ModelSerializer):
    bank = BankSerializer()  # To include bank details

    class Meta:
        model = ExchangeRate
        fields = ['id', 'bank', 'currency', 'buying_rate', 'selling_rate', 'transactional_buying_rate', 'transactional_selling_rate', 'date', 'updated_at']

class FuelSerializer(serializers.ModelSerializer):
    difference = serializers.SerializerMethodField()

    class Meta:
        model = Fuel
        fields = ['name', 'value', 'difference', 'date']

    def get_difference(self, obj):
        # Calculate the difference between current value and previous value
        if obj.previous_value is not None:
            return obj.value - obj.previous_value
        return None  # or return 0 if you prefer to show 0 when there's no previous value
    
class FuelChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuel
        fields = ['name', 'value', 'date']

