# Generated by Django 5.0.3 on 2024-04-04 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo_de_caixa', '0032_rename_vencimento_cashflowentry_due_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cashflowentry',
            old_name='descricao',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='tabelatemporaria',
            old_name='descricao',
            new_name='description',
        ),
    ]
