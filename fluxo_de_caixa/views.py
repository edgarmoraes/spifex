import uuid
import json
from decimal import Decimal
from datetime import datetime
from itertools import groupby
from django.db.models import Sum
from django.utils import timezone
from collections import OrderedDict
from django.contrib import messages
from django.dispatch import receiver
from django.http import JsonResponse
from realizado.models import Tabela_realizado
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from chart_of_accounts.models import Chart_of_accounts
from django.db.models.signals import post_save, post_delete
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tabela_fluxo, TabelaTemporaria, Totais_mes_fluxo, Bancos

def cash_flow(request):
    if request.method == "GET":
        return display_cash_flow(request)
    elif request.method == "POST":
        return process_cash_flow(request)

def display_cash_flow(request):
    bancos_ativos = Bancos.objects.filter(status=True)
    tabela_fluxo_list = Tabela_fluxo.objects.all().order_by('vencimento', '-valor', 'descricao')
    totais_mes_fluxo = Totais_mes_fluxo.objects.all()
    chart_of_accounts_queryset = Chart_of_accounts.objects.all().order_by('-subgroup', 'account')
    
    # Agrupando as contas por subgroup usando OrderedDict para manter a ordem
    accounts_by_subgroup = OrderedDict()
    for account in chart_of_accounts_queryset:
        if account.subgroup not in accounts_by_subgroup:
            accounts_by_subgroup[account.subgroup] = []
        accounts_by_subgroup[account.subgroup].append(account)

    tabela_fluxo_list = list(tabela_fluxo_list)

    lancamentos_com_totais = []
    for key, group in groupby(tabela_fluxo_list, key=lambda x: x.vencimento.strftime('%Y-%m')):
        lista_grupo = list(group)
        lancamentos_com_totais.extend(lista_grupo)

        total_debito = sum(item.valor for item in lista_grupo if item.natureza == 'Débito')
        total_credito = sum(item.valor for item in lista_grupo if item.natureza == 'Crédito')
        saldo_total = total_credito - total_debito

        lancamentos_com_totais.append({
            'vencimento': datetime.strptime(key + "-01", '%Y-%m-%d'),
            'descricao': 'Total do Mês',
            'debito': total_debito,
            'credito': total_credito,
            'saldo': saldo_total,
            'is_total': True,
        })

    context = {
        'Tabela_fluxo_list': lancamentos_com_totais,
        'totais_mes_fluxo': totais_mes_fluxo,
        'bancos': bancos_ativos,
        'accounts_by_subgroup': accounts_by_subgroup,  # Passando o OrderedDict para o contexto
    }
    return render(request, 'fluxo_de_caixa.html', context)

def process_cash_flow(request):
    if 'transferencias' in request.POST and request.POST['transferencias'] == 'transferencia':
        return process_transfer(request)
    else:
        dados = extract_form_data(request)
    if dados['lancamento_id']:
        if dados['parcelas_total'] > 1:
            if dados['parcelas_total_originais'] > 1:
                update_existing_flow(dados)  # Manter parcelas_total se for uma série de parcelas
            else:
                # Criar novos fluxos se o número de parcelas foi alterado para mais de um
                Tabela_fluxo.objects.filter(id=dados['lancamento_id']).delete()
                create_new_flows(dados)
        else:
            update_existing_flow(dados)  # Atualização normal para lançamentos de uma única parcela
    else:
        create_new_flows(dados)
    return redirect(request.path)

def extract_form_data(request):
    """Extrai e retorna os dados do formulário."""
    natureza = 'Crédito' if 'salvar_recebimento' in request.POST else 'Débito'

    if natureza == 'Crédito':
        conta_contabil_uuid = request.POST.get('conta_contabil_uuid_recebimentos')
        conta_contabil_nome = request.POST.get('conta_contabil_nome_recebimentos')
    else:
        conta_contabil_uuid = request.POST.get('conta_contabil_uuid_pagamentos')
        conta_contabil_nome = request.POST.get('conta_contabil_nome_pagamentos')
    
    # Escolhe o campo de ID correto com base na natureza da transação
    lancamento_id_recebimentos = request.POST.get('lancamento_id_recebimentos')
    lancamento_id_pagamentos = request.POST.get('lancamento_id_pagamentos')
    
    lancamento_id = None  # Inicialmente definido como None
    
    if natureza == 'Crédito' and lancamento_id_recebimentos:
        lancamento_id = int(lancamento_id_recebimentos)
    elif natureza == 'Débito' and lancamento_id_pagamentos:
        lancamento_id = int(lancamento_id_pagamentos)
    
    # Verifica e processa o campo 'vencimento'
    vencimento_str = request.POST.get('vencimento')
    vencimento = datetime.strptime(vencimento_str, '%Y-%m-%d') if vencimento_str else None

    valor_str = request.POST.get('valor', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    valor = float(valor_str) if valor_str else 0.00

    # Processa outros campos com segurança
    descricao = request.POST.get('descricao', '')
    observacao = request.POST.get('observacao', '')
    parcelas = request.POST.get('parcelas', '1')
    parcelas_total = int(parcelas) if parcelas.isdigit() else 1
    parcelas_total_originais = int(request.POST.get('parcelas_total_originais', '1'))
    tags = request.POST.get('tags', '')

    # Retorna um dicionário com os dados processados
    return {
        'vencimento': vencimento,
        'descricao': descricao,
        'observacao': observacao,
        'valor': valor,
        'conta_contabil_uuid': conta_contabil_uuid,
        'conta_contabil_nome': conta_contabil_nome,
        'parcelas_total': parcelas_total,
        'parcelas_total_originais': parcelas_total_originais,
        'tags': tags,
        'lancamento_id': lancamento_id,
        'natureza': natureza,
    }

def update_existing_flow(dados):
    # Busca o fluxo de caixa pelo ID
    cash_flow_table = get_object_or_404(Tabela_fluxo, id=dados['lancamento_id'])
    
    # Atualiza campos comuns diretamente
    cash_flow_table.vencimento = dados['vencimento']
    cash_flow_table.descricao = dados['descricao']
    cash_flow_table.observacao = dados['observacao']
    cash_flow_table.valor = dados['valor']
    cash_flow_table.natureza = dados['natureza']
    # Não altera parcelas_total se já é parte de uma série de parcelas
    if cash_flow_table.parcelas_total <= 1 or 'parcelas_total' not in dados:
        cash_flow_table.parcelas_total = dados.get('parcelas_total', cash_flow_table.parcelas_total)
    cash_flow_table.tags = dados['tags']

    # Atualiza a conta contábil e seu UUID
    cash_flow_table.conta_contabil = dados['conta_contabil_nome']
    cash_flow_table.uuid_conta_contabil = dados['conta_contabil_uuid']

    # Salva as alterações no banco de dados
    cash_flow_table.save()

def create_new_flows(dados, iniciar_desde_o_atual=False):
    if 'vencimento' not in dados or dados['vencimento'] is None:
        return JsonResponse({'error': 'Data de vencimento é necessária.'}, status=400)

    parcela_inicial = dados.get('parcela_atual', 1)
    total_parcelas = dados['parcelas_total']

    # Verifica se 'vencimento' já é um object datetime.datetime
    if isinstance(dados['vencimento'], datetime):
        vencimento_base = dados['vencimento'].date()
    else:
        # Converte de string para datetime.datetime se 'vencimento' for uma string
        vencimento_base = datetime.strptime(dados['vencimento'], '%Y-%m-%d').date()

    for i in range(parcela_inicial, total_parcelas + 1):
        vencimento_parcela = vencimento_base + relativedelta(months=i - parcela_inicial)
        Tabela_fluxo.objects.create(
            vencimento=vencimento_parcela,
            descricao=dados['descricao'],
            observacao=dados['observacao'],
            valor=dados['valor'],
            conta_contabil=dados['conta_contabil_nome'],  # Usar o nome da conta contábil
            uuid_conta_contabil=dados['conta_contabil_uuid'],  # Armazenar o UUID da conta contábil
            parcela_atual=i,
            parcelas_total=total_parcelas,
            tags=dados['tags'],
            natureza=dados['natureza'],
            data_criacao=datetime.now()
        )

@csrf_exempt
def delete_entries(request):
    if request.method == 'POST':
        ids_para_apagar = extract_ids_to_delete(request)

        # Verifica se algum dos lançamentos selecionados tem uuid_correlacao não nulo
        lancamentos_com_dependencia = Tabela_fluxo.objects.filter(id__in=ids_para_apagar, uuid_correlacao__isnull=False)

        if lancamentos_com_dependencia.exists():
            # Retorna uma mensagem de erro se algum lançamento tem dependência
            return JsonResponse({'status': 'error', 'message': 'Este lançamento tem dependências liquidadas.'}, status=400)
        
        # Procede com a exclusão se todos os lançamentos puderem ser excluídos
        process_ids(ids_para_apagar)
        return JsonResponse({'status': 'success'})

def extract_ids_to_delete(request):
    """ Extrai os IDs do corpo da solicitação """
    data = json.loads(request.body)
    return data.get('ids', [])  # Retorna uma lista vazia se 'ids' não estiver presente

def process_ids(ids_para_apagar):
    """ Processa cada ID para apagar o object correspondente e criar um registro na TabelaTemporaria """
    for id_str in ids_para_apagar:
        try:
            id = int(id_str)  # Convertendo o ID para inteiro
            object = Tabela_fluxo.objects.get(id=id)
            create_temporary_record(object)
            object.delete()  # Apagando o object original
        except Tabela_fluxo.DoesNotExist:
            # Se o ID não for encontrado, pula para o próximo
            continue

def create_temporary_record(object):
    """ Cria um novo registro na TabelaTemporaria com base no object da Tabela_fluxo """
    TabelaTemporaria.objects.create(
        vencimento=object.vencimento,
        descricao=object.descricao,
        observacao=object.observacao,
        valor=object.valor,
        conta_contabil=object.conta_contabil,
        uuid_conta_contabil=object.uuid_conta_contabil,
        parcela_atual=object.parcela_atual,
        parcelas_total=object.parcelas_total,
        tags=object.tags,
        natureza=object.natureza,
        data_criacao=object.data_criacao
    )

def process_transfer(request):
    banco_saida_data = request.POST.get('banco_saida').split('|')
    banco_entrada_data = request.POST.get('banco_entrada').split('|')

    if len(banco_saida_data) == 2 and len(banco_entrada_data) == 2:
        banco_saida_id, banco_saida_nome = banco_saida_data
        banco_entrada_id, banco_entrada_nome = banco_entrada_data

    data_transferencia = request.POST.get('data')
    valor_transferencia_str = request.POST.get('valor', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    valor_transferencia = Decimal(valor_transferencia_str) if valor_transferencia_str else 0.00
    observacao = request.POST.get('observacao')
    correlacao_id = uuid.uuid4()
    
    data_liquidacao = datetime.strptime(data_transferencia, '%Y-%m-%d')

    if banco_saida_id == banco_entrada_id:
        messages.error(request, "O banco de saída não pode ser igual ao banco de entrada. Por favor, selecione bancos diferentes.")
        return redirect('fluxo_de_caixa')
    
    # Cria o lançamento de saída
    lancamento_saida = Tabela_realizado(
        vencimento=data_liquidacao,
        descricao=f'Transferência para {banco_entrada_nome}',
        banco_id_liquidacao=banco_saida_id,
        banco_liquidacao=banco_saida_nome,
        observacao=observacao,
        valor=valor_transferencia,
        conta_contabil='Transferência Saída',
        parcela_atual=1,
        parcelas_total=1,
        tags='Transferência',
        natureza='Débito',
        original_data_criacao=datetime.now(),
        data_liquidacao=data_liquidacao,
        uuid_correlacao=correlacao_id
    )
    lancamento_saida.save()

    # Cria o lançamento de entrada
    lancamento_entrada = Tabela_realizado(
        vencimento=data_liquidacao,
        descricao=f'Transferência de {banco_saida_nome}',
        banco_id_liquidacao=banco_entrada_id,
        banco_liquidacao=banco_entrada_nome,
        observacao=observacao,
        valor=valor_transferencia,
        conta_contabil='Transferência Entrada',
        parcela_atual=1,
        parcelas_total=1,
        tags='Transferência',
        natureza='Crédito',
        original_data_criacao=datetime.now(),
        data_liquidacao=data_liquidacao,
        uuid_correlacao=correlacao_id
    )
    lancamento_entrada.save()

    return redirect(request.path)

@csrf_exempt
def process_settlement(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        resposta = {'status': 'success', 'messages': []}

        for item in dados:
            try:
                registro_original = Tabela_fluxo.objects.get(id=item['id'])
                valor_total = registro_original.valor
                valor_parcial = Decimal(item.get('valor_parcial', 0))
                is_liquidacao_parcial = valor_parcial > 0 and valor_parcial <= valor_total
                completando_liquidacao = valor_parcial == valor_total

                uuid_correlacao = registro_original.uuid_correlacao
                if is_liquidacao_parcial:
                    if not uuid_correlacao:
                        # Caso seja a primeira liquidação parcial
                        uuid_correlacao = uuid.uuid4()
                        registro_original.uuid_correlacao = uuid_correlacao
                        registro_original.save()
                    if valor_parcial < valor_total:
                        novo_valor = valor_total - valor_parcial
                        registro_original.valor = novo_valor
                        registro_original.save()
                    # Se for a última liquidação parcial, o UUID já está definido

                data_liquidacao_aware = timezone.make_aware(datetime.strptime(item['data_liquidacao'], '%Y-%m-%d'))
                numero_liquidacao = Tabela_realizado.objects.filter(uuid_correlacao=uuid_correlacao).count() + 1 if uuid_correlacao else 1

                descricao_atualizada = registro_original.descricao
                if is_liquidacao_parcial:
                    descricao_atualizada += f" | Parcela ({numero_liquidacao})"

                Tabela_realizado.objects.create(
                    fluxo_id=registro_original.id,
                    vencimento=registro_original.vencimento,
                    descricao=descricao_atualizada,
                    observacao=item['observacao'],
                    valor=valor_parcial if is_liquidacao_parcial else valor_total,
                    conta_contabil=registro_original.conta_contabil,
                    uuid_conta_contabil=registro_original.uuid_conta_contabil,
                    parcela_atual=registro_original.parcela_atual,
                    parcelas_total=registro_original.parcelas_total,
                    tags=registro_original.tags,
                    natureza=registro_original.natureza,
                    original_data_criacao=registro_original.data_criacao,
                    data_liquidacao=data_liquidacao_aware,
                    banco_liquidacao=item.get('banco_liquidacao', ''),
                    banco_id_liquidacao=item.get('banco_id_liquidacao', ''),
                    uuid_correlacao=uuid_correlacao,
                    uuid_correlacao_parcelas=uuid_correlacao
                )

                # Remove o registro original se for uma liquidação total ou a última liquidação parcial
                if completando_liquidacao or not is_liquidacao_parcial:
                    registro_original.delete()

            except Tabela_fluxo.DoesNotExist:
                resposta['messages'].append(f'Registro {item["id"]} não encontrado.')
                continue

        return JsonResponse(resposta)
    else:
        return JsonResponse({'status': 'method not allowed'}, status=405)


# SIGNAL HANDLERS ############################################################################

@receiver(post_save, sender=Tabela_fluxo)
def save_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

@receiver(post_delete, sender=Tabela_fluxo)
def delete_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

def recalculate_totals():
    """ Sinal para atualizar Totais_mes_fluxo quando um FluxoDeCaixa for salvo """
    # Apaga todos os registros existentes em Totais_mes_fluxo
    Totais_mes_fluxo.objects.all().delete()

    # Encontra todas as datas únicas de vencimento em Tabela_fluxo
    datas_unicas = Tabela_fluxo.objects.dates('vencimento', 'month', order='ASC')

    for data_unica in datas_unicas:
        inicio_mes = data_unica
        fim_mes = inicio_mes + relativedelta(months=1, days=-1)

        # Calcula os totais de crédito e débito para cada mês
        total_credito = Tabela_fluxo.objects.filter(
            vencimento__range=(inicio_mes, fim_mes),
            natureza='Crédito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        total_debito = Tabela_fluxo.objects.filter(
            vencimento__range=(inicio_mes, fim_mes),
            natureza='Débito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        # Cria um novo registro em Totais_mes_fluxo para cada mês
        Totais_mes_fluxo.objects.create(
            data_formatada=inicio_mes.strftime('%b/%Y'),
            inicio_mes=inicio_mes,
            fim_mes=fim_mes,
            total_credito=total_credito,
            total_debito=total_debito,
            saldo_mensal=total_credito - total_debito
        )

# FUNÇÕES ÚNICAS ############################################################################

def filter_months(request):
    totais_mes_fluxo = Totais_mes_fluxo.objects.all().order_by('data_formatada')
    context = {'totais_mes_fluxo': totais_mes_fluxo}
    return render(request, 'fluxo_de_caixa.html', context)

def display_banks(request):
    bancos = Bancos.objects.all()
    return render(request, 'fluxo_de_caixa.html', {'bancos': bancos})
