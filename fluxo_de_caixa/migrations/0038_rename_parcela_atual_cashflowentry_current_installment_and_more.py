# Generated by Django 5.0.3 on 2024-04-05 01:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo_de_caixa', '0037_rename_uuid_conta_contabil_cashflowentry_uuid_general_ledger_account_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cashflowentry',
            old_name='parcela_atual',
            new_name='current_installment',
        ),
        migrations.RenameField(
            model_name='tabelatemporaria',
            old_name='parcela_atual',
            new_name='current_installment',
        ),
    ]