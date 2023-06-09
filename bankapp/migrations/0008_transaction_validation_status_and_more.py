# Generated by Django 4.1.5 on 2023-05-08 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0007_alter_transaction_transaction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='validation_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Validated', 'Validated'), ('Rejected', 'Rejected')], default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('Deposit', 'Deposit'), ('Withdrawal', 'Withdrawal'), ('Airtime', 'Airtime'), ('Sent', 'Sent'), ('Received', 'Received'), ('Utility', 'Utility')], max_length=10),
        ),
    ]
