# Generated by Django 4.1.5 on 2023-06-08 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0019_loan_interest_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='interest_rate',
            field=models.DecimalField(decimal_places=1, default=14.0, max_digits=5),
        ),
    ]
