# Generated by Django 5.0.1 on 2024-01-19 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0020_totaismes_fim_mes_totaismes_inicio_mes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tabela_fluxo',
            name='parcelas',
        ),
        migrations.AddField(
            model_name='tabela_fluxo',
            name='parcela_atual',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tabela_fluxo',
            name='parcelas_total',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tabelatemporaria',
            name='parcela_atual',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tabelatemporaria',
            name='parcelas_total',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
