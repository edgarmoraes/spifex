# Generated by Django 5.0.3 on 2024-03-22 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realizado', '0012_tabela_realizado_banco_id_liquidacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='tabela_realizado',
            name='uuid_conta_contabil',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]