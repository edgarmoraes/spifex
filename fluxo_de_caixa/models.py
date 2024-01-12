from django.db import models
from datetime import datetime, timedelta

class Tabela_fluxo(models.Model):
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 100)
    observacao = models.CharField(max_length = 100)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    conta_contabil = models.CharField(max_length = 100)
    parcelas = models.CharField(max_length=50)
    tags = models.CharField(max_length = 100)
    natureza = models.CharField(max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)

class TabelaTemporaria(models.Model):
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 100)
    observacao = models.CharField(max_length = 100)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    conta_contabil = models.CharField(max_length = 100)
    parcelas = models.CharField(max_length=50)
    tags = models.CharField(max_length = 100)
    natureza = models.CharField(max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)
    # Campo para rastrear quando a entrada foi movida
    movido_em = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def remover_antigos():
        # Define o limite de tempo em 1 hora
        limite_tempo = datetime.now() - timedelta(hours=1)
        TabelaTemporaria.objects.filter(movido_em__lt=limite_tempo).delete()