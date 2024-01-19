# Generated by Django 5.0.1 on 2024-01-15 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo_de_caixa', '0017_totaismes_delete_dataunica'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bancos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banco', models.CharField(max_length=100)),
                ('agencia', models.CharField(max_length=100)),
                ('conta', models.CharField(max_length=100)),
                ('saldo_inicial', models.DecimalField(decimal_places=2, max_digits=13)),
            ],
        ),
    ]