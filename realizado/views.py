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
    if request.method != 'POST':
        return JsonResponse({'status': 'method not allowed'}, status=405)

    dados = json.loads(request.body)
    ids_selecionados = [item['id'] for item in dados]

    for item in dados:
        registro_original = Tabela_realizado.objects.filter(id=item['id']).first()
        if not registro_original:
            continue

        uuid_correlacao = registro_original.uuid_correlacao
        uuid_correlacao_parcelas = registro_original.uuid_correlacao_parcelas

        if not uuid_correlacao:
            criar_fluxo_com_registro(registro_original)
        elif uuid_correlacao and uuid_correlacao_parcelas is None:
            # Aqui é onde implementamos a lógica específica: Deletar todos os lançamentos em Tabela_realizado que compartilham o mesmo uuid_correlacao
            Tabela_realizado.objects.filter(uuid_correlacao=uuid_correlacao).delete()
        else:
            processar_lancamentos_com_uuids_selecionados(uuid_correlacao, uuid_correlacao_parcelas, ids_selecionados, registro_original)

    return JsonResponse({'status': 'success'})

def criar_fluxo_com_registro(registro):
    Tabela_fluxo.objects.create(
        vencimento=registro.vencimento,
        descricao=registro.descricao,
        observacao=registro.observacao,
        valor=registro.valor,
        conta_contabil=registro.conta_contabil,
        parcela_atual=registro.parcela_atual,
        parcelas_total=registro.parcelas_total,
        tags=registro.tags,
        natureza=registro.natureza,
        data_criacao=registro.original_data_criacao,
    )
    registro.delete()

def processar_lancamentos_com_uuids_selecionados(uuid_correlacao, uuid_correlacao_parcelas, ids_selecionados, registro_original):
    mais_registros = Tabela_realizado.objects.filter(uuid_correlacao=uuid_correlacao, uuid_correlacao_parcelas=uuid_correlacao_parcelas).exclude(id__in=ids_selecionados).exists()
    existe_no_fluxo = Tabela_fluxo.objects.filter(uuid_correlacao=uuid_correlacao).exists()

    registros_selecionados = Tabela_realizado.objects.filter(id__in=ids_selecionados, uuid_correlacao=uuid_correlacao, uuid_correlacao_parcelas=uuid_correlacao_parcelas)
    valor_total_selecionados = registros_selecionados.aggregate(Sum('valor'))['valor__sum'] or 0

    if mais_registros and existe_no_fluxo:
        unificar_lancamentos_no_fluxo(uuid_correlacao, valor_total_selecionados)
    elif not mais_registros and existe_no_fluxo:
        unificar_lancamentos_no_fluxo(uuid_correlacao, valor_total_selecionados, excluir_uuid=True)
    elif not mais_registros and not existe_no_fluxo:
        criar_fluxo_com_registro_unificado(registros_selecionados.first(), valor_total_selecionados, manter_uuid=False)
    elif mais_registros and not existe_no_fluxo:
        criar_fluxo_com_registro_unificado(registros_selecionados.first(), valor_total_selecionados, manter_uuid=True)

    registros_selecionados.delete()

def unificar_lancamentos_no_fluxo(uuid_correlacao, valor_total, excluir_uuid=False):
    fluxo = Tabela_fluxo.objects.get(uuid_correlacao=uuid_correlacao)
    fluxo.valor += valor_total
    if excluir_uuid:
        fluxo.uuid_correlacao = None
    fluxo.save()

def criar_fluxo_com_registro_unificado(registro, valor_total, manter_uuid=False):
    Tabela_fluxo.objects.create(
        vencimento=registro.vencimento,
        descricao=registro.descricao,
        observacao=registro.observacao,
        valor=valor_total,
        conta_contabil=registro.conta_contabil,
        parcela_atual=registro.parcela_atual,
        parcelas_total=registro.parcelas_total,
        tags=registro.tags,
        natureza=registro.natureza,
        data_criacao=registro.original_data_criacao,
        uuid_correlacao=registro.uuid_correlacao if manter_uuid else None
    )

@receiver(post_delete, sender=Tabela_realizado)
def atualizar_saldo_banco_apos_remocao(sender, instance, **kwargs):
    try:
        banco = Bancos.objects.get(id=instance.banco_id_liquidacao)  # Modificado para usar ID
        if instance.natureza == 'Crédito':
            banco.saldo_atual -= instance.valor  # Subtrai para créditos
        else:  # Débito
            banco.saldo_atual += instance.valor  # Adiciona para débitos
        banco.save()
    except Bancos.DoesNotExist:
        pass  # Tratar o caso em que o banco não é encontrado, se necessário