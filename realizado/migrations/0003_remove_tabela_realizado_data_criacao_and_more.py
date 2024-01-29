# Generated by Django 5.0.1 on 2024-01-28 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realizado', '0002_tabela_realizado_data_liquidacao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tabela_realizado',
            name='data_criacao',
        ),
        migrations.AddField(
            model_name='tabela_realizado',
            name='fluxo_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tabela_realizado',
            name='original_data_criacao',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
