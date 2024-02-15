from django.db import models
from datetime import datetime, timedelta
from decimal import Decimal

class Tabela_fluxo(models.Model):
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 100)
    observacao = models.CharField(max_length = 100)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    conta_contabil = models.CharField(max_length = 100)
    parcela_atual = models.IntegerField()
    parcelas_total = models.IntegerField()
    tags = models.CharField(max_length = 100)
    natureza = models.CharField(max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)

class Totais_mes_fluxo(models.Model):
    inicio_mes = models.DateField(null=True, blank=True)
    fim_mes = models.DateField(null=True, blank=True)
    data_formatada = models.CharField(max_length=255, unique=True)
    total_credito = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    total_debito = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    saldo_mensal = models.DecimalField(max_digits=13, decimal_places=2, default=0)

    def __str__(self):
        return self.data_formatada

class TabelaTemporaria(models.Model):
    vencimento = models.DateField()
    descricao = models.CharField(max_length = 100)
    observacao = models.CharField(max_length = 100)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    conta_contabil = models.CharField(max_length = 100)
    parcela_atual = models.IntegerField()
    parcelas_total = models.IntegerField()
    tags = models.CharField(max_length = 100)
    natureza = models.CharField(max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)
    movido_em = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def remover_antigos():
        # Define o limite de tempo em 1 hora
        limite_tempo = datetime.now() - timedelta(hours=1)
        TabelaTemporaria.objects.filter(movido_em__lt=limite_tempo).delete()

class Bancos(models.Model):
    banco = models.CharField(max_length = 100)
    agencia = models.CharField(max_length = 100)
    conta = models.CharField(max_length = 100)
    saldo_inicial = models.DecimalField(max_digits=13, decimal_places=2)
    saldo_atual = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    saldo_consolidado = models.DecimalField(max_digits=13, decimal_places=2, default=0) 
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Verifica se a instância já existe (edição) ou é nova
        if self.pk:
            # Instância existente: Carrega o objeto atual do banco para comparação
            obj_atual = Bancos.objects.get(pk=self.pk)
            if self.saldo_inicial != obj_atual.saldo_inicial:
                # Se o saldo_inicial foi alterado, atualiza apenas o saldo_consolidado
                # saldo_atual não é modificado, mas recalcula saldo_consolidado
                self.saldo_consolidado = Decimal(self.saldo_inicial) + Decimal(self.saldo_atual) - Decimal(obj_atual.saldo_inicial)
        else:
            # Nova instância: Inicializa saldo_atual e saldo_consolidado com saldo_inicial
            self.saldo_atual = Decimal(self.saldo_inicial)
            self.saldo_consolidado = Decimal(self.saldo_inicial)

        super(Bancos, self).save(*args, **kwargs)