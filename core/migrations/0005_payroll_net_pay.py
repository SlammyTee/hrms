# Generated by Django 5.2 on 2025-06-03 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_payroll_pay_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='net_pay',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
