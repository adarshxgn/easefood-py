# Generated by Django 5.1.4 on 2025-03-19 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_orders_table_number_alter_orders_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='description',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
