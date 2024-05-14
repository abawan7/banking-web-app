# Generated by Django 5.0.3 on 2024-03-25 17:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_accounts'),
    ]

    operations = [
        migrations.CreateModel(
            name='ATMcards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16, unique=True)),
                ('pin', models.CharField(max_length=4)),
                ('expiry_date', models.DateField()),
                ('card_type', models.CharField(choices=[('Visa', 'Visa'), ('Mastercard', 'Mastercard'), ('American Express', 'American Express')], max_length=20)),
                ('is_active', models.BooleanField(default=False)),
                ('accounts', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.accounts')),
            ],
        ),
    ]