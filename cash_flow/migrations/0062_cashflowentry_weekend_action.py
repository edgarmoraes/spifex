# Generated by Django 5.0.3 on 2024-04-27 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0061_cashflowentry_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashflowentry',
            name='weekend_action',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
