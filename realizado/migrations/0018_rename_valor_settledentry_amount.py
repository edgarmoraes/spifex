# Generated by Django 5.0.3 on 2024-04-04 00:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realizado', '0017_rename_observacao_settledentry_observation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='settledentry',
            old_name='valor',
            new_name='amount',
        ),
    ]
