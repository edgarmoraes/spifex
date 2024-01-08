from django.db import models

class recebimentos(models.Model):
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 100)
    observacao = models.CharField(max_length = 100)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    conta_contabil = models.CharField(max_length = 100)
    parcelas = models.IntegerField()
    tags = models.CharField(max_length = 100)
    data_criacao = models.DateTimeField()
