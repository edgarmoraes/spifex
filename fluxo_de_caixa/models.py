from django.db import models

class recebimentos(models.Model):
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 50)
    data_criacao = models.DateTimeField()