# Generated by Django 5.0.3 on 2024-05-13 20:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0023_alter_beneficiary_account_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(default="", max_length=150, unique=True),
        ),
    ]
