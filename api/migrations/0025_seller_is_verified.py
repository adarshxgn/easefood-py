# Generated by Django 5.1.4 on 2025-03-18 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_remove_orders_food_items_remove_orders_prep_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
