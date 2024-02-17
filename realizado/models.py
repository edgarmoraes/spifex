import uuid
from django.db import models
from fluxo_de_caixa.models import Bancos

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
    data_liquidacao = models.DateTimeField()
    banco_liquidacao = models.CharField(max_length=255, null=True, blank=True)
    uuid_correlacao = models.UUIDField(null=True, blank=True)  # Campo novo para agrupar transferências
    uuid_correlacao_parcelas = models.UUIDField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Chama o método save original para salvar a transação
        self.atualizar_saldo_banco()
    
    def atualizar_saldo_banco(self):
        # Assume que 'banco_liquidacao' armazena o nome do banco
        banco = Bancos.objects.get(banco=self.banco_liquidacao)
        if self.natureza == 'Crédito':
            banco.saldo_atual += self.valor
        else:  # Débito
            banco.saldo_atual -= self.valor
        banco.save()

class Totais_mes_realizado(models.Model):
    inicio_mes = models.DateField(null=True, blank=True)
    fim_mes = models.DateField(null=True, blank=True)
    data_formatada = models.CharField(max_length=255, unique=True)
    total_credito = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    total_debito = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    saldo_mensal = models.DecimalField(max_digits=13, decimal_places=2, default=0)

    def __str__(self):
        return self.data_formatada