from django.db import models
from datetime import datetime, timedelta

class CashFlowEntry(models.Model):
    due_date = models.DateField()
    description = models.CharField(max_length = 100)
    observation = models.CharField(max_length = 100)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    general_ledger_account = models.CharField(max_length = 100)
    current_installment = models.IntegerField()
    total_installments = models.IntegerField()
    tags = models.CharField(max_length = 100)
    transaction_type = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    uuid_correlation = models.UUIDField(null=True, blank=True)
    uuid_general_ledger_account = models.UUIDField(null=True, blank=True)

class MonthsListCashFlow(models.Model):
    start_of_month = models.DateField(null=True, blank=True)
    end_of_month = models.DateField(null=True, blank=True)
    formatted_date = models.CharField(max_length=255, unique=True)
    total_credit = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    total_debit = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    monthly_balance = models.DecimalField(max_digits=13, decimal_places=2, default=0)

    def __str__(self):
        return self.formatted_date

class TemporaryTable(models.Model):
    due_date = models.DateField()
    description = models.CharField(max_length = 100)
    observation = models.CharField(max_length = 100)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    general_ledger_account = models.CharField(max_length = 100)
    uuid_general_ledger_account = models.UUIDField(null=True, blank=True)
    current_installment = models.IntegerField()
    total_installments = models.IntegerField()
    tags = models.CharField(max_length = 100)
    transaction_type = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    moved_in = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def remover_antigos():
        # Define o limite de tempo em 1 hora
        limite_tempo = datetime.now() - timedelta(hours=1)
        TemporaryTable.objects.filter(moved_in__lt=limite_tempo).delete()

class Banks(models.Model):
    banco = models.CharField(max_length = 100)
    agencia = models.CharField(max_length = 100)
    conta = models.CharField(max_length = 100)
    saldo_inicial = models.DecimalField(max_digits=13, decimal_places=2)
    current_balance = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    saldo_consolidado = models.DecimalField(max_digits=13, decimal_places=2, default=0) 
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # No momento da criação do objeto, isso garantirá que saldo_consolidado = saldo_inicial
        if not self.pk:  # Checa se é uma nova instância
            self.saldo_consolidado = self.saldo_inicial
        else:
            # Para instâncias existentes, atualiza saldo_consolidado com base no current_balance
            self.saldo_consolidado = self.saldo_inicial + self.current_balance
        super().save(*args, **kwargs)

class Departamentos(models.Model):
    departamento = models.CharField(max_length = 256)
    uuid_departamento = models.UUIDField(null=True, blank=True)