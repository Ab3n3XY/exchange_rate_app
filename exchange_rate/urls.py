from django.urls import path
from .views import BankListView, BankDetailView, ExchangeRateListView, ExchangeRateDetailView

urlpatterns = [
    path('banks/', BankListView.as_view(), name='bank-list'),
    path('banks/<int:pk>/', BankDetailView.as_view(), name='bank-detail'),
    path('exchange-rates/', ExchangeRateListView.as_view(), name='exchange-rate-list'),
    path('exchange-rates/<int:pk>/', ExchangeRateDetailView.as_view(), name='exchange-rate-detail'),
]
