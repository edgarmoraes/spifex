from django.shortcuts import render
from django.db.models import Sum
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from fluxo_de_caixa.models import Tabela_fluxo, Bancos
from .models import Tabela_realizado, Totais_mes_realizado

def realizado(request):
    if request.method == "GET":
        return exibir_realizado(request)

def exibir_realizado(request):
    """ Exibe a lista de fluxos de caixa junto com os totais de cada mês e bancos """
    bancos_ativos = Bancos.objects.filter(status=True)
    saldo_total_bancos = bancos_ativos.aggregate(Sum('saldo_inicial'))['saldo_inicial__sum'] or 0
    Tabela_realizado_list = Tabela_realizado.objects.all().order_by('vencimento')
    calcular_saldo_acumulado(Tabela_realizado_list, saldo_total_bancos)
    totais_mes_realizado = Totais_mes_realizado.objects.all()
    context = {
        'Tabela_realizado_list': Tabela_realizado_list,
        'totais_mes_realizado': totais_mes_realizado,
        'bancos': bancos_ativos,
        'saldo_total_bancos': saldo_total_bancos
    }
    return render(request, 'realizado.html', context)

def calcular_saldo_acumulado(Tabela_realizado_list, saldo_inicial):
    """ Calcula o saldo acumulado para cada entrada em uma lista de fluxos de caixa.
    :param Tabela_realizado_list: QuerySet de objetos Tabela_realizado.
    :return: None. Modifica cada objeto Tabela_realizado adicionando um atributo 'saldo' """
    saldo_total = saldo_inicial
    for realizado in Tabela_realizado_list:
        if realizado.natureza == 'Débito':
            saldo_total -= realizado.valor
        else:
            saldo_total += realizado.valor
        realizado.saldo = saldo_total

def exibir_bancos(request):
    bancos = Bancos.objects.all()
    return render(request, 'realizado.html', {'bancos': bancos})

@csrf_exempt
def processar_liquidacao(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        ids_para_excluir = []

        for item in dados:
            registro_original = Tabela_fluxo.objects.get(id=item['id'])

        for item in dados:
            novo_registro = Tabela_realizado.objects.create(
                fluxo_id=registro_original.id,
                vencimento=datetime.strptime(item['vencimento'], '%d/%m/%Y').date(),
                descricao=registro_original.descricao,
                observacao=registro_original.observacao,
                valor=registro_original.valor,
                conta_contabil=registro_original.conta_contabil,
                parcela_atual=registro_original.parcela_atual,
                parcelas_total=registro_original.parcelas_total,
                tags=registro_original.tags,
                natureza=registro_original.natureza,
                original_data_criacao=registro_original.data_criacao,
                data_liquidacao=datetime.now(),
            )
            if novo_registro:
                ids_para_excluir.append(item['id'])

        Tabela_fluxo.objects.filter(id__in=ids_para_excluir).delete()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid method'}, status=405)


@receiver(post_save, sender=Tabela_realizado)
def save_update_data_unica_realizado(sender, instance, **kwargs):
    data_formatada = instance.vencimento.strftime('%b/%Y')
    atualizar_totais_mes_realizado(data_formatada)

@receiver(post_delete, sender=Tabela_realizado)
def delete_update_data_unica_realizado(sender, instance, **kwargs):
    data_formatada = instance.vencimento.strftime('%b/%Y')
    if not Tabela_realizado.objects.filter(vencimento__year=instance.vencimento.year, vencimento__month=instance.vencimento.month).exists():
        Totais_mes_realizado.objects.filter(data_formatada=data_formatada).delete()
    else:
        atualizar_totais_mes_realizado(data_formatada)

def atualizar_totais_mes_realizado(data_formatada):
    inicio_mes = datetime.strptime(data_formatada, '%b/%Y').replace(day=1)
    fim_mes = inicio_mes + relativedelta(months=1, days=-1)

    total_credito = Tabela_realizado.objects.filter(
        vencimento__range=[inicio_mes, fim_mes],
        natureza='Crédito'
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    total_debito = Tabela_realizado.objects.filter(
        vencimento__range=[inicio_mes, fim_mes],
        natureza='Débito'
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    saldo_mensal = total_credito - total_debito

    Totais_mes_realizado.objects.update_or_create(
        data_formatada=data_formatada,
        defaults={
            'inicio_mes': inicio_mes,
            'fim_mes': fim_mes,
            'total_credito': total_credito,
            'total_debito': total_debito,
            'saldo_mensal': total_credito - total_debito
        }
    )

def meses_filtro_realizado(request):
    totais_mes_realizado = Totais_mes_realizado.objects.all().order_by('data_formatada')
    context = {'totais_mes_realizado': totais_mes_realizado}
    return render(request, 'realizado.html', context)