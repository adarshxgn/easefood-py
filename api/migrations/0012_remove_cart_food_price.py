# Generated by Django 5.1.4 on 2025-03-05 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_cart_id_alter_food_is_available_checkout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='food_price',
        ),
    ]
