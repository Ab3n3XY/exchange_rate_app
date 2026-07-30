from django.contrib import admin
from .models import Bank, ExchangeRate, Fuel

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number', 'website')
    search_fields = ('name', 'contact_number', 'website')

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'buying_rate', 'selling_rate', 'transactional_buying_rate', 'transactional_selling_rate', 'date', 'bank')
    search_fields = ('currency', 'bank__name')
    list_filter = ('date', 'bank')

@admin.register(Fuel)
class FuelAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'date')
    search_fields = ('name', 'value', 'date')