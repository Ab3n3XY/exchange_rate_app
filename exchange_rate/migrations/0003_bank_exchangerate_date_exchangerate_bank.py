# Generated by Django 5.0.7 on 2024-07-31 16:57

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange_rate', '0002_exchangerate_transactional_buying_rate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('contact_number', models.CharField(max_length=20)),
                ('website', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='exchangerate',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='exchangerate',
            name='bank',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='exchange_rates', to='exchange_rate.bank'),
        ),
    ]
