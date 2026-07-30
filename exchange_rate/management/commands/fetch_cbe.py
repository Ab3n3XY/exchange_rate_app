from django.core.management.base import BaseCommand
import requests
from datetime import date, datetime
from exchange_rate.models import ExchangeRate

class Command(BaseCommand):
    help = 'Fetch and save exchange rates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Specify the date to fetch exchange rates for (format: YYYY-MM-DD)',
        )

    def handle(self, *args, **kwargs):
        date_arg = kwargs['date']
        if date_arg:
            try:
                specified_date = datetime.strptime(date_arg, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write("Error: Invalid date format. Use YYYY-MM-DD.")
                return
        else:
            specified_date = date.today()

        url = "https://www.combanketh.et/cbeapi/daily-exchange-rates/?_limit=1"
        desired_currencies = ['USD', 'GBP', 'EUR', 'AED', 'SAR', 'CNY', 'CHF', 'CAD']
        url_with_date = f"{url}&Date={specified_date.isoformat()}"

        response = requests.get(url_with_date)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                filtered_data = []
                for item in data:
                    if isinstance(item, dict):
                        exchange_rates = item.get("ExchangeRate", [])
                        for ex_rate in exchange_rates:
                            currency = ex_rate.get("currency", {})
                            if currency.get("CurrencyCode") in desired_currencies:
                                filtered_data.append({
                                    **ex_rate,
                                    'Date': specified_date.isoformat()  # Ensure the date is correctly passed
                                })
                self.save_to_model(filtered_data)
            else:
                self.stdout.write("Error: The fetched data is not a list.")
        else:
            self.stdout.write(f"Error fetching data: {response.status_code}")

    def create_exchange_rate(self, data):
        currency = data.get("currency", {})
        date_str = data.get("Date", "")
        try:
            exchange_date = datetime.fromisoformat(date_str).date() if date_str else date.today()
        except ValueError:
            exchange_date = date.today()

        return {
            'bank_id': 1,
            'currency': currency.get("CurrencyCode", ""),
            'buying_rate': data.get("cashBuying", 0.0),
            'selling_rate': data.get("cashSelling", 0.0),
            'transactional_buying_rate': data.get("transactionalBuying", 0.0),
            'transactional_selling_rate': data.get("transactionalSelling", 0.0),
            'date': exchange_date,
        }

    def save_to_model(self, exchange_rate_data):
        for data in exchange_rate_data:
            exchange_rate = self.create_exchange_rate(data)
            obj, created = ExchangeRate.objects.update_or_create(
                currency=exchange_rate['currency'],
                date=exchange_rate['date'],
                bank_id=1,
                defaults={
                    'bank_id': 1,
                    'buying_rate': exchange_rate['buying_rate'],
                    'selling_rate': exchange_rate['selling_rate'],
                    'transactional_buying_rate': exchange_rate['transactional_buying_rate'],
                    'transactional_selling_rate': exchange_rate['transactional_selling_rate']
                }
            )
            self.stdout.write(f"Saved {obj} to the database.")

