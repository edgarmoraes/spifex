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
    document_type = models.CharField(null=True, max_length=50)
    department = models.JSONField(null=True, blank=True)
    department_percentage = models.JSONField(null=True, blank=True)
    project = models.CharField(null=True, max_length=50)
    notes = models.CharField(max_length=256)
    periods = models.CharField(max_length=50)
    weekend_action = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    uuid_installments_correlation = models.UUIDField(null=True, blank=True)
    uuid_general_ledger_account = models.UUIDField(blank=True)
    uuid_document_type = models.UUIDField(null=True, blank=True)
    uuid_department = models.JSONField(null=True, blank=True)
    uuid_project = models.UUIDField(null=True, blank=True)
    uuid_transference = models.JSONField(null=True, blank=True)
    uuid_partial_settlement_correlation = models.UUIDField(null=True, blank=True)

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
    current_installment = models.IntegerField()
    total_installments = models.IntegerField()
    tags = models.CharField(max_length = 100)
    transaction_type = models.CharField(max_length=50)
    document_type = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    notes = models.CharField(max_length=256)
    periods = models.CharField(max_length=50)
    weekend_action = models.CharField(max_length=50)
    uuid_general_ledger_account = models.UUIDField(null=True, blank=True)
    uuid_document_type = models.UUIDField(null=True, blank=True)
    uuid_department = models.UUIDField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    moved_in = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def remove_old():
        # Define o limite de tempo em 1 hora
        time_limit = datetime.now() - timedelta(hours=1)
        TemporaryTable.objects.filter(moved_in__lt=time_limit).delete()

class Banks(models.Model):
    banco = models.CharField(max_length = 100)
    bank_branch = models.CharField(max_length = 100)
    bank_account = models.CharField(max_length = 100)
    initial_balance = models.DecimalField(max_digits=13, decimal_places=2)
    current_balance = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    consolidated_balance = models.DecimalField(max_digits=13, decimal_places=2, default=0) 
    bank_status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # No momento da criação do objeto, isso garantirá que consolidated_balance = initial_balance
        if not self.pk:  # Checa se é uma nova instância
            self.consolidated_balance = self.initial_balance
        else:
            # Para instâncias existentes, atualiza consolidated_balance com base no current_balance
            self.consolidated_balance = self.initial_balance + self.current_balance
        super().save(*args, **kwargs)

class Departments(models.Model):
    department = models.CharField(max_length = 256)
    uuid_department = models.UUIDField(null=True, blank=True)

class DocumentType(models.Model):
    document_type = models.CharField(max_length = 256)
    uuid_document_type = models.UUIDField(null=True, blank=True)

class Inventory(models.Model):
    inventory_item_code = models.CharField(max_length=255)
    inventory_item = models.CharField(max_length=255)
    inventory_quantity = models.PositiveIntegerField(default=0)
    uuid_inventory_item = models.UUIDField(null=True, blank=True)
