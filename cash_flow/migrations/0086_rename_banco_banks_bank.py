# Generated by Django 5.0.6 on 2024-06-25 00:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0085_cashflowentry_entity_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='banks',
            old_name='banco',
            new_name='bank',
        ),
    ]
