# Generated by Django 4.1.5 on 2023-04-23 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0003_myuser_account_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=10),
        ),
    ]
