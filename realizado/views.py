import json
from django.db.models import Sum
from django.shortcuts import render
from django.dispatch import receiver
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from fluxo_de_caixa.models import Tabela_fluxo, Bancos
from .models import Tabela_realizado, Totais_mes_realizado
from django.db.models.signals import post_save, post_delete

def realizado(request):
    if request.method == "GET":
        return exibir_realizado(request)

def exibir_realizado(request):
    """ Exibe a lista de fluxos de caixa junto com os totais de cada mês """
    bancos_ativos = Bancos.objects.filter(status=True)

    Tabela_realizado_list = Tabela_realizado.objects.all().order_by('data_liquidacao', '-valor', 'descricao')

    totais_mes_realizado = Totais_mes_realizado.objects.all()
    context = {
        'Tabela_realizado_list': Tabela_realizado_list,
        'totais_mes_realizado': totais_mes_realizado,
        'bancos': bancos_ativos,
    }
    return render(request, 'realizado.html', context)


def exibir_bancos(request):
    bancos = Bancos.objects.all()
    return render(request, 'realizado.html', {'bancos': bancos})


@receiver(post_save, sender=Tabela_realizado)
def save_update_data_unica_realizado(sender, instance, **kwargs):
    recalcular_totais_realizado()

@receiver(post_delete, sender=Tabela_realizado)
def delete_update_data_unica_realizado(sender, instance, **kwargs):
    recalcular_totais_realizado()

def recalcular_totais_realizado():
    # Apaga todos os registros existentes em Totais_mes_realizado
    Totais_mes_realizado.objects.all().delete()

    # Encontra todas as datas únicas de vencimento em Tabela_realizado
    datas_unicas = Tabela_realizado.objects.dates('data_liquidacao', 'month', order='ASC')

    for data_unica in datas_unicas:
        inicio_mes = data_unica
        fim_mes = inicio_mes + relativedelta(months=1, days=-1)

        # Calcula os totais de crédito e débito para cada mês
        total_credito = Tabela_realizado.objects.filter(
            vencimento__range=(inicio_mes, fim_mes),
            natureza='Crédito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        total_debito = Tabela_realizado.objects.filter(
            vencimento__range=(inicio_mes, fim_mes),
            natureza='Débito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        # Cria um novo registro em Totais_mes_realizado para cada mês
        Totais_mes_realizado.objects.create(
            data_formatada=inicio_mes.strftime('%b/%Y'),
            inicio_mes=inicio_mes,
            fim_mes=fim_mes,
            total_credito=total_credito,
            total_debito=total_debito,
            saldo_mensal=total_credito - total_debito
        )

def meses_filtro_realizado(request):
    totais_mes_realizado = Totais_mes_realizado.objects.all().order_by('data_formatada')
    context = {'totais_mes_realizado': totais_mes_realizado}
    return render(request, 'realizado.html', context)


@csrf_exempt
def processar_retorno(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        ids_para_excluir = []

        # Itera sobre os dados recebidos para criar novos registros em Tabela_fluxo
        for item in dados:
            # Busca o registro original em Tabela_realizado usando o ID fornecido
            registro_original = Tabela_realizado.objects.get(id=item['id'])

            # Cria um novo registro em Tabela_fluxo com os dados de Tabela_realizado
            novo_registro_fluxo = Tabela_fluxo.objects.create(
                vencimento=registro_original.vencimento,
                descricao=registro_original.descricao,
                observacao=registro_original.observacao,
                valor=registro_original.valor,
                conta_contabil=registro_original.conta_contabil,
                parcela_atual=registro_original.parcela_atual,
                parcelas_total=registro_original.parcelas_total,
                tags=registro_original.tags,
                natureza=registro_original.natureza,
                data_criacao=registro_original.original_data_criacao  # Supondo que há este campo para manter a data de criação original
            )

            # Adiciona o ID do registro original à lista de IDs para exclusão
            if novo_registro_fluxo:
                ids_para_excluir.append(item['id'])

        # Exclui os registros originais em Tabela_realizado
        Tabela_realizado.objects.filter(id__in=ids_para_excluir).delete()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid method'}, status=405)

@receiver(post_delete, sender=Tabela_realizado)
def atualizar_saldo_banco_apos_remocao(sender, instance, **kwargs):
    try:
        banco = Bancos.objects.get(banco=instance.banco_liquidacao)
        if instance.natureza == 'Crédito':
            banco.saldo_atual -= instance.valor  # Subtrai o valor do saldo atual para créditos
        else:  # Débito
            banco.saldo_atual += instance.valor  # Adiciona o valor ao saldo atual para débitos
        banco.save()
    except Bancos.DoesNotExist:
        pass  # Tratar o caso em que o banco não é encontrado, se necessário