# Generated by Django 5.0.1 on 2024-02-15 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo_de_caixa', '0026_rename_saldo_total_bancos_saldo_consolidado'),
    ]

    operations = [
        migrations.AddField(
            model_name='tabela_fluxo',
            name='uuid_correlacao',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]