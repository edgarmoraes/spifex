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
        ('Transferência entre Contas', 'Transferência entre Contas'),  # Adicionado à lista de escolhas
    ]

    nature = models.CharField(max_length=255, choices=CREDITO_DEBITO_CHOICES, editable=False)
    group = models.CharField(max_length=255, choices=GROUP_CHOICES)
    subgroup = models.CharField(max_length=255)  # Subgrupo
    account = models.CharField(max_length=255)  # Nome da conta
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def save(self, *args, **kwargs):
        # Não altera 'nature' se for 'Transferência entre Contas'
        if self.group != 'Transferência entre Contas':
            if self.group in ['Receitas Operacionais', 'Receitas Não Operacionais']:
                self.nature = 'Crédito'
            else:
                self.nature = 'Débito'
        super(Chart_of_accounts, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.account} ({self.nature})"