# Generated by Django 5.0.4 on 2024-05-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="transaction_id",
            field=models.CharField(
                default="b570018c-d32e-42e9-a92f-3fc2a105eb5f",
                max_length=100,
                unique=True,
            ),
        ),
    ]
