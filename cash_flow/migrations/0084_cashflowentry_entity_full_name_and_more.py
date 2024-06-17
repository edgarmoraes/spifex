# Generated by Django 5.0.6 on 2024-06-17 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0083_rename_uuid_entities_item_entities_uuid_entities'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashflowentry',
            name='entity_full_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cashflowentry',
            name='entity_tax_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cashflowentry',
            name='uuid_entity',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
