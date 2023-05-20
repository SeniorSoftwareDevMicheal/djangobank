# Generated by Django 4.1.5 on 2023-05-13 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0009_remove_transaction_validation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='is_deposit_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='DepositValidationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_validated', models.BooleanField(default=False)),
                ('validation_date', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]