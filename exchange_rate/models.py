from django.db import models
import datetime

class Bank(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    website = models.URLField()

    def __str__(self):
        return self.name
    
class ExchangeRate(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='exchange_rates', default=1)
    currency = models.CharField(max_length=10)
    buying_rate = models.DecimalField(max_digits=10, decimal_places=4)
    selling_rate = models.DecimalField(max_digits=10, decimal_places=4)
    transactional_buying_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    transactional_selling_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    date = models.DateField(default=datetime.date.today)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.currency} ({self.bank.name}) - Buying: {self.buying_rate}, Selling: {self.selling_rate}"
