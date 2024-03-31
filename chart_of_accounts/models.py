from django.db import models
import uuid

class Chart_of_accounts(models.Model):
    CREDITO_DEBITO_CHOICES = [
        ('Crédito', 'Crédito'),
        ('Débito', 'Débito'),
    ]
    GROUP_CHOICES = [
        ('Receitas Operacionais', 'Receitas Operacionais'),
        ('Receitas Não Operacionais', 'Receitas Não Operacionais'),
        ('Despesas Operacionais', 'Despesas Operacionais'),
        ('Despesas Não Operacionais', 'Despesas Não Operacionais'),
    ]

    nature = models.CharField(max_length=255, choices=CREDITO_DEBITO_CHOICES, editable=False)
    group = models.CharField(max_length=255, choices=GROUP_CHOICES)
    subgroup = models.CharField(max_length=255)
    account = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def save(self, *args, **kwargs):
        if self.group in ['Receitas Operacionais', 'Receitas Não Operacionais']:
            self.nature = 'Crédito'
        else:
            self.nature = 'Débito'
        super(Chart_of_accounts, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.account} ({self.nature})"
    
class Groups_list(models.Model):
    groups_list = models.CharField(max_length=255)
    
class Subgroups_list(models.Model):
    subgroups_list = models.CharField(max_length=255)
    
class Accounts_list(models.Model):
    accounts_list = models.CharField(max_length=255)
    uuid_accounts_list = models.CharField(max_length=255)