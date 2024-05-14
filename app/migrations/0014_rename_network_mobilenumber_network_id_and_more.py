# Generated by Django 5.0.3 on 2024-05-08 14:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0013_remove_mobilenumber_network_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="mobilenumber",
            old_name="network",
            new_name="network_id",
        ),
        migrations.RemoveField(
            model_name="mobiletopup",
            name="mobile_number",
        ),
        migrations.AddField(
            model_name="mobilenumber",
            name="name",
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name="mobiletopup",
            name="mobile_number_id",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.mobilenumber",
            ),
        ),
    ]