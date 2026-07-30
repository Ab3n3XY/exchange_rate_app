from django.urls import path
from .views import (BankListView, BankDetailView, ExchangeRateListView, ExchangeRateDetailView,
                     update_exchange_rates, ExchangeRateChartView, fetch_exchange_rates_view,
                     update_exchange_rate,FuelListView, FuelChartView)

urlpatterns = [
    path('banks/', BankListView.as_view(), name='bank-list'),
    path('banks/<int:pk>/', BankDetailView.as_view(), name='bank-detail'),
    path('exchange-rates/', ExchangeRateListView.as_view(), name='exchange-rate-list'),
    path('chart/', ExchangeRateChartView.as_view(), name='chart'),
    path('exchange-rates/<int:pk>/', ExchangeRateDetailView.as_view(), name='exchange-rate-detail'),
    path('update-rates/', update_exchange_rates, name='update_exchange_rates'),
    path('fetch/', fetch_exchange_rates_view, name='fetch_exchange_rates'),
    path('update-exchange-rate/', update_exchange_rate, name='update_exchange_rate'),
    path('fuels/', FuelListView.as_view(), name='fuel-list'),
    path('fuel-chart/', FuelChartView.as_view(), name='fuel-chart'),
]
