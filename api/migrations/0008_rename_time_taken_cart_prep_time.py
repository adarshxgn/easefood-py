# Generated by Django 5.1.4 on 2025-01-27 05:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_cart_status_cart_time_taken'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='time_taken',
            new_name='prep_time',
        ),
    ]
