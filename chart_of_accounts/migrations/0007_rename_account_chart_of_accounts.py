# Generated by Django 5.0.3 on 2024-03-19 00:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chart_of_accounts', '0006_account_delete_exceldata_delete_exceldocument'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Account',
            new_name='Chart_of_accounts',
        ),
    ]
