# Generated by Django 5.0.6 on 2024-05-19 20:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realizado', '0002_settledentry_uuid_transference'),
    ]

    operations = [
        migrations.RenameField(
            model_name='settledentry',
            old_name='uuid_correlation_installments',
            new_name='uuid_partial_settlement_correlation',
        ),
    ]