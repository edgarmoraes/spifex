# Generated by Django 5.0.3 on 2024-04-07 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realizado', '0024_rename_original_data_criacao_settledentry_original_creation_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='settledentry',
            old_name='uuid_correlacao',
            new_name='uuid_correlation',
        ),
        migrations.RenameField(
            model_name='settledentry',
            old_name='uuid_correlacao_parcelas',
            new_name='uuid_correlation_parcelas',
        ),
    ]
