from rest_framework import generics
from rest_framework.response import Response
from .models import Bank, ExchangeRate, Fuel
from .serializers import BankSerializer, ExchangeRateSerializer, ExchangeChartRateSerializer, FuelSerializer, FuelChartSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
import datetime
from django.db.models import OuterRef, Subquery, F, ExpressionWrapper, fields, Value, Case, When, Max, Min
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse
from django.core.management import call_command
from datetime import date
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from decimal import Decimal

class BankListView(generics.ListCreateAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class BankDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class ExchangeRateListView(generics.ListAPIView):
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        date = self.request.query_params.get('date')
        current_date = timezone.now().date()

        if date:
            try:
                date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                if date > current_date:
                    raise ValidationError("Future dates are not allowed.")
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        else:
            date = current_date

        # Query for the latest rate on or before the requested date
        latest_rates_subquery = ExchangeRate.objects.filter(
            bank=OuterRef('bank'),
            currency=OuterRef('currency'),
            date__lte=date
        ).order_by('-date')

        # Query for the rate from the day before the latest rate date
        previous_rates_subquery = ExchangeRate.objects.filter(
            bank=OuterRef('bank'),
            currency=OuterRef('currency'),
            date__lt=OuterRef('date')
        ).order_by('-date')

        queryset = ExchangeRate.objects.filter(
            id=Subquery(latest_rates_subquery.values('id')[:1])
        ).annotate(
            previous_buying_rate=Subquery(previous_rates_subquery.values('buying_rate')[:1]),
            previous_selling_rate=Subquery(previous_rates_subquery.values('selling_rate')[:1]),
            previous_transactional_buying_rate=Subquery(previous_rates_subquery.values('transactional_buying_rate')[:1]),
            previous_transactional_selling_rate=Subquery(previous_rates_subquery.values('transactional_selling_rate')[:1]),
            is_requested_date=Case(
                When(date=date, then=Value(True)),
                default=Value(False),
                output_field=fields.BooleanField()
            ),
            buying_rate_difference=Case(
                When(is_requested_date=False, then=Value(0.0000)),
                default=ExpressionWrapper(
                    F('buying_rate') - F('previous_buying_rate'),
                    output_field=fields.FloatField()
                ),
                output_field=fields.FloatField()
            ),
            selling_rate_difference=Case(
                When(is_requested_date=False, then=Value(0.0000)),
                default=ExpressionWrapper(
                    F('selling_rate') - F('previous_selling_rate'),
                    output_field=fields.FloatField()
                ),
                output_field=fields.FloatField()
            ),
            transactional_buying_rate_difference=Case(
                When(is_requested_date=False, then=Value(0.0000)),
                default=ExpressionWrapper(
                    F('transactional_buying_rate') - F('previous_transactional_buying_rate'),
                    output_field=fields.FloatField()
                ),
                output_field=fields.FloatField()
            ),
            transactional_selling_rate_difference=Case(
                When(is_requested_date=False, then=Value(0.0000)),
                default=ExpressionWrapper(
                    F('transactional_selling_rate') - F('previous_transactional_selling_rate'),
                    output_field=fields.FloatField()
                ),
                output_field=fields.FloatField()
            )
        )

        return queryset

class ExchangeRateChartView(generics.ListAPIView):
    serializer_class = ExchangeChartRateSerializer

    def get_queryset(self):
        currency = self.request.query_params.get('currency')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        date = self.request.query_params.get('date')
        banks = self.request.query_params.get('banks', '').split(',')
        current_date = timezone.now().date()

        if start_date and end_date:
            # Validate and process date range
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

                if start_date > end_date:
                    raise ValidationError("Start date must be before or equal to end date.")
                if start_date > current_date or end_date > current_date:
                    raise ValidationError("Dates cannot be in the future.")
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

            queryset = ExchangeRate.objects.filter(
                currency=currency,
                date__range=(start_date, end_date),
                bank__name__in=banks
            )

        elif date:
            # Validate and process single date
            try:
                date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                if date > current_date:
                    raise ValidationError("Future dates are not allowed.")
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

            latest_rates_subquery = ExchangeRate.objects.filter(
                bank=OuterRef('bank'),
                currency=OuterRef('currency'),
                date__lte=date
            ).order_by('-date')

            queryset = ExchangeRate.objects.filter(
                id=Subquery(latest_rates_subquery.values('id')[:1])
            )

        else:
            # Default behavior: Fetch latest rates for the past two days
            two_days_ago = current_date - timedelta(days=2)

            latest_rates_subquery = ExchangeRate.objects.filter(
                bank=OuterRef('bank'),
                currency=OuterRef('currency'),
                date__gte=two_days_ago
            ).order_by('-date')

            queryset = ExchangeRate.objects.filter(
                id=Subquery(latest_rates_subquery.values('id')[:1])
            )

        if currency:
            queryset = queryset.filter(currency=currency)

        if banks:
            queryset = queryset.filter(bank__name__in=banks)

        return queryset

class ExchangeRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def update_exchange_rates(request):
    banks = Bank.objects.all()
    currencies = ['USD', 'EUR', 'GBP', 'CHF', 'CAD', 'SAR', 'AED', 'CNY']
    today = datetime.date.today().strftime('%Y-%m-%d')
    success = False

    if request.method == 'POST':
        date = request.POST.get('date')
        bank_id = request.POST.get('bank')
        bank = Bank.objects.get(id=bank_id)

        for currency in currencies:
            buying_rate = request.POST.get(f'buying_rate_{currency}')
            selling_rate = request.POST.get(f'selling_rate_{currency}')
            transactional_buying_rate = request.POST.get(f'transactional_buying_rate_{currency}')
            transactional_selling_rate = request.POST.get(f'transactional_selling_rate_{currency}')

            if buying_rate or selling_rate or transactional_buying_rate or transactional_selling_rate:
                ExchangeRate.objects.update_or_create(
                    bank=bank,
                    currency=currency,
                    date=date,
                    defaults={
                        'buying_rate': buying_rate if buying_rate else None,
                        'selling_rate': selling_rate if selling_rate else None,
                        'transactional_buying_rate': transactional_buying_rate if transactional_buying_rate else None,
                        'transactional_selling_rate': transactional_selling_rate if transactional_selling_rate else None,
                    }
                )
        success = True

    # Determine which banks have been updated for today
    updated_banks = set(
        ExchangeRate.objects.filter(
            date=today
        ).values_list('bank', flat=True)
    )

    banks_with_update_flag = [
        {
            'id': bank.id,
            'name': bank.name,
            'updated_for_today': bank.id in updated_banks
        }
        for bank in banks
    ]

    return render(request, 'update_exchange_rates.html', {
        'banks': banks_with_update_flag,
        'currencies': currencies,
        'today': today,
        'success': success,
    })


@user_passes_test(is_admin)
def fetch_exchange_rates_view(request):
    if request.method == "POST":
        date = request.POST.get('date', '')
        try:
            call_command('fetch_cbe', date=date)
            return JsonResponse({'message': 'Exchange rates updated successfully'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return render(request, 'fetch.html')

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def update_exchange_rate(request):
    logger.info(f"Request body: {request.body}")
    logger.info(f"Request headers: {request.headers}")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Data received: {data}")
            for rate in data:
                ExchangeRate.objects.update_or_create(
                    currency=rate['currency'],
                    date=date.today(),
                    bank_id=rate['bank_id'],
                    defaults={
                        'buying_rate': rate['buying'],
                        'selling_rate': rate['selling'],
                        'transactional_buying_rate': rate['transactional_buying'],
                        'transactional_selling_rate': rate['transactional_selling'],
                        'date': date.today()
                    }
                )
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        logger.error(f"Invalid request method: {request.method}")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



class FuelListView(generics.ListAPIView):
    serializer_class = FuelSerializer

    def get_queryset(self):
        date_param = self.request.query_params.get('date', None)
        current_date = timezone.now().date()

        if date_param:
            try:
                date = parse_date(date_param)
                if not date:
                    raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
                if date > current_date:
                    raise ValidationError("Future dates are not allowed.")
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        else:
            date = current_date

        # Fetch the latest date per fuel type on or before the requested date
        latest_fuels = []
        fuel_types = Fuel.FUEL_CHOICES
        for fuel_type, _ in fuel_types:
            latest_date = Fuel.objects.filter(
                name=fuel_type, date__lte=date
            ).aggregate(latest_date=Max('date'))['latest_date']

            if latest_date:
                latest_fuel = Fuel.objects.filter(
                    name=fuel_type, date=latest_date
                ).first()

                previous_fuel_subquery = Fuel.objects.filter(
                    name=fuel_type,
                    date__lt=latest_date
                ).order_by('-date').values('value')[:1]

                latest_fuel.previous_value = previous_fuel_subquery[0]['value'] if previous_fuel_subquery else Decimal('0.0000')
                latest_fuel.value_difference = latest_fuel.value - latest_fuel.previous_value
                latest_fuel.is_requested_date = (latest_fuel.date == date)
                latest_fuels.append(latest_fuel)

        return latest_fuels

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Find previous and next available dates
        requested_date = parse_date(self.request.query_params.get('date', None)) or timezone.now().date()

        previous_date = Fuel.objects.filter(date__lt=requested_date).aggregate(previous_date=Max('date'))['previous_date']
        next_date = Fuel.objects.filter(date__gt=requested_date).aggregate(next_date=Min('date'))['next_date']

        return Response({
            'fuels': serializer.data,
            'previous_date': previous_date,
            'next_date': next_date,
        })

class FuelChartView(generics.ListAPIView):
    serializer_class = FuelChartSerializer

    def get_queryset(self):
        fuel_type = self.request.query_params.get('fuel_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        date = self.request.query_params.get('date')
        current_date = timezone.now().date()

        if start_date and end_date:
            # Validate and process date range
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

                if start_date > end_date:
                    raise ValidationError("Start date must be before or equal to end date.")
                if start_date > current_date or end_date > current_date:
                    raise ValidationError("Dates cannot be in the future.")
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

            queryset = Fuel.objects.filter(
                name=fuel_type,
                date__range=(start_date, end_date)
            )

        elif date:
            # Validate and process single date
            try:
                date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                if date > current_date:
                    raise ValidationError("Future dates are not allowed.")
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

            latest_prices_subquery = Fuel.objects.filter(
                name=OuterRef('name'),
                date__lte=date
            ).order_by('-date')

            queryset = Fuel.objects.filter(
                id=Subquery(latest_prices_subquery.values('id')[:1])
            )

        else:
            # No specific date range or single date provided, fetch all data up to the current date
            queryset = Fuel.objects.filter(
                date__lte=current_date
            )

        if fuel_type:
            queryset = queryset.filter(name=fuel_type)

        return queryset