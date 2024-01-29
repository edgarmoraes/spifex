from django.db import models

class Tabela_realizado(models.Model):
    fluxo_id = models.IntegerField(null=True, blank=True)
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 100)
    observacao = models.CharField(max_length = 100)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    conta_contabil = models.CharField(max_length = 100)
    parcela_atual = models.IntegerField()
    parcelas_total = models.IntegerField()
    tags = models.CharField(max_length = 100)
    natureza = models.CharField(max_length=50)
    original_data_criacao = models.DateTimeField(null=True, blank=True)
    data_liquidacao = models.DateTimeField(auto_now_add=True)
    banco_liquidacao = models.CharField(max_length = 100)

class Totais_mes_realizado(models.Model):
    inicio_mes = models.DateField(null=True, blank=True)
    fim_mes = models.DateField(null=True, blank=True)
    data_formatada = models.CharField(max_length=255, unique=True)
    total_credito = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    total_debito = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    saldo_mensal = models.DecimalField(max_digits=13, decimal_places=2, default=0)

    def __str__(self):
        return self.data_formatada