from django.contrib import admin
from .models import Bank, ExchangeRate

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number', 'website')
    search_fields = ('name', 'contact_number', 'website')

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'buying_rate', 'selling_rate', 'transactional_buying_rate', 'transactional_selling_rate', 'date', 'bank')
    search_fields = ('currency', 'bank__name')
    list_filter = ('date', 'bank')
