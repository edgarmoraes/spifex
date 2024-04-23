# Generated by Django 5.0.1 on 2024-01-08 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0002_recebimentos_data_criacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='recebimentos',
            name='conta_contabil',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recebimentos',
            name='observacao',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recebimentos',
            name='parcelas',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recebimentos',
            name='tags',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recebimentos',
            name='valor',
            field=models.DecimalField(decimal_places=2, default=0.00, max_digits=13),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recebimentos',
            name='descricao',
            field=models.CharField(max_length=100),
        ),
    ]