# Generated by Django 5.0.3 on 2024-04-07 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo_de_caixa', '0049_rename_months_list_cash_flow_monthslistcashflow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bancos',
            old_name='saldo_atual',
            new_name='current_balance',
        ),
        migrations.RenameField(
            model_name='temporarytable',
            old_name='movido_em',
            new_name='moved_in',
        ),
    ]