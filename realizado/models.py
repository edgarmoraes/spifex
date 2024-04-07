import uuid
from django.db import models
from fluxo_de_caixa.models import Bancos

class SettledEntry(models.Model):
    fluxo_id = models.IntegerField(null=True, blank=True)
    due_date = models.DateField()
    description = models.CharField(max_length = 100)
    observation = models.CharField(max_length = 100)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    general_ledger_account = models.CharField(max_length = 100)
    current_installment = models.IntegerField()
    total_installments = models.IntegerField()
    tags = models.CharField(max_length = 100)
    transaction_type = models.CharField(max_length=50)
    original_creation_date = models.DateTimeField(null=True, blank=True)
    data_liquidacao = models.DateTimeField()
    banco_liquidacao = models.CharField(max_length=255, null=True, blank=True)
    banco_id_liquidacao = models.IntegerField(null=True, blank=True)
    uuid_correlation = models.UUIDField(null=True, blank=True)
    uuid_correlation_parcelas = models.UUIDField(null=True, blank=True)
    uuid_general_ledger_account = models.UUIDField(null=True, blank=True)

    _skip_update_saldo = False

    def save(self, *args, **kwargs):
        if not self._skip_update_saldo:
            self.atualizar_saldo_banco()
        super().save(*args, **kwargs)
    
    def atualizar_saldo_banco(self):
        banco = Bancos.objects.get(id=self.banco_id_liquidacao)  # Modificado para usar ID
        if self.transaction_type == 'Crédito':
            banco.current_balance += self.amount
        else:  # Débito
            banco.current_balance -= self.amount
        banco.save()
        pass

class MonthsListSettled(models.Model):
    start_of_month = models.DateField(null=True, blank=True)
    end_of_month = models.DateField(null=True, blank=True)
    formatted_date = models.CharField(max_length=255, unique=True)
    total_credit = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    total_debit = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    monthly_balance = models.DecimalField(max_digits=13, decimal_places=2, default=0)

    def __str__(self):
        return self.formatted_date