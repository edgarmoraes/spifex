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
from realizado.models import SettledEntry
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from chart_of_accounts.models import Chart_of_accounts
from django.db.models.signals import post_save, post_delete
from django.shortcuts import render, redirect, get_object_or_404
from .models import CashFlowEntry, TabelaTemporaria, Totais_mes_fluxo, Bancos

def cash_flow(request):
    if request.method == "GET":
        return display_cash_flow(request)
    elif request.method == "POST":
        return process_cash_flow(request)

def display_cash_flow(request):
    active_banks = Bancos.objects.filter(status=True)
    cash_flow_table_list = CashFlowEntry.objects.all().order_by('due_date', '-valor', 'descricao')
    months_list = Totais_mes_fluxo.objects.all()
    chart_of_accounts_queryset_list = Chart_of_accounts.objects.all().order_by('-subgroup', 'account')
    
    # Agrupando as contas por subgroup usando OrderedDict para manter a ordem
    accounts_by_subgroup = OrderedDict()
    for account in chart_of_accounts_queryset_list:
        if account.subgroup not in accounts_by_subgroup:
            accounts_by_subgroup[account.subgroup] = []
        accounts_by_subgroup[account.subgroup].append(account)

    cash_flow_table_list = list(cash_flow_table_list)

    entries_with_totals = []
    for key, group in groupby(cash_flow_table_list, key=lambda x: x.due_date.strftime('%Y-%m')):
        group_list = list(group)
        entries_with_totals.extend(group_list)

        total_debit = sum(item.valor for item in group_list if item.natureza == 'Débito')
        total_credit = sum(item.valor for item in group_list if item.natureza == 'Crédito')
        total_balance = total_credit - total_debit

        entries_with_totals.append({
            'due_date': datetime.strptime(key + "-01", '%Y-%m-%d'),
            'descricao': 'Total do Mês',
            'debito': total_debit,
            'credito': total_credit,
            'saldo': total_balance,
            'is_total': True,
        })

    context = {
        'Cash_flow_table_list': entries_with_totals,
        'Months_list': months_list,
        'Banks_list': active_banks,
        'Accounts_by_subgroup_list': accounts_by_subgroup,
    }
    return render(request, 'cash_flow.html', context)

def process_cash_flow(request):
    if 'transferencias' in request.POST and request.POST['transferencias'] == 'transferencia':
        return process_transfer(request)
    else:
        form_data = extract_form_data(request)
    if form_data['lancamento_id']:
        if form_data['parcelas_total'] > 1:
            if form_data['parcelas_total_originais'] > 1:
                update_existing_flow(form_data)  # Manter parcelas_total se for uma série de parcelas
            else:
                # Criar novos fluxos se o número de parcelas foi alterado para mais de um
                CashFlowEntry.objects.filter(id=form_data['lancamento_id']).delete()
                create_new_flows(form_data)
        else:
            update_existing_flow(form_data)
    else:
        create_new_flows(form_data)
    return redirect(request.path)

def extract_form_data(request):
    """Extrai e retorna os dados do formulário."""
    transaction_type = 'Crédito' if 'salvar_recebimento' in request.POST else 'Débito'

    if transaction_type == 'Crédito':
        account_uuid = request.POST.get('conta_contabil_uuid_recebimentos')
        account_name = request.POST.get('conta_contabil_nome_recebimentos')
    else:
        account_uuid = request.POST.get('conta_contabil_uuid_pagamentos')
        account_name = request.POST.get('conta_contabil_nome_pagamentos')
    
    # Escolhe o campo de ID correto com base na natureza da transação
    receipt_entry_id = request.POST.get('lancamento_id_recebimentos')
    payment_entry_id = request.POST.get('lancamento_id_pagamentos')
    
    entry_id = None  # Inicialmente definido como None
    
    if transaction_type == 'Crédito' and receipt_entry_id:
        entry_id = int(receipt_entry_id)
    elif transaction_type == 'Débito' and payment_entry_id:
        entry_id = int(payment_entry_id)
    
    # Verifica e processa o campo 'due_date'
    due_date_str = request.POST.get('due_date')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

    transaction_amount_str = request.POST.get('valor', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    transaction_amount = float(transaction_amount_str) if transaction_amount_str else 0.00

    # Processa outros campos com segurança
    entry_description = request.POST.get('descricao', '')
    entry_observation = request.POST.get('observacao', '')
    installment = request.POST.get('parcelas', '1')
    total_installments = int(installment) if installment.isdigit() else 1
    original_total_installments = int(request.POST.get('parcelas_total_originais', '1'))
    entry_tags = request.POST.get('tags', '')

    # Retorna um dicionário com os dados processados
    return {
        'due_date': due_date,
        'descricao': entry_description,
        'observacao': entry_observation,
        'valor': transaction_amount,
        'conta_contabil_uuid': account_uuid,
        'conta_contabil_nome': account_name,
        'parcelas_total': total_installments,
        'parcelas_total_originais': original_total_installments,
        'tags': entry_tags,
        'lancamento_id': entry_id,
        'natureza': transaction_type,
    }

def update_existing_flow(form_data):
    # Busca o fluxo de caixa pelo ID
    cash_flow_table = get_object_or_404(CashFlowEntry, id=form_data['lancamento_id'])
    
    # Atualiza campos comuns diretamente
    cash_flow_table.due_date = form_data['due_date']
    cash_flow_table.descricao = form_data['descricao']
    cash_flow_table.observacao = form_data['observacao']
    cash_flow_table.valor = form_data['valor']
    cash_flow_table.natureza = form_data['natureza']
    # Não altera parcelas_total se já é parte de uma série de parcelas
    if cash_flow_table.parcelas_total <= 1 or 'parcelas_total' not in form_data:
        cash_flow_table.parcelas_total = form_data.get('parcelas_total', cash_flow_table.parcelas_total)
    cash_flow_table.tags = form_data['tags']

    # Atualiza a conta contábil e seu UUID
    cash_flow_table.conta_contabil = form_data['conta_contabil_nome']
    cash_flow_table.uuid_conta_contabil = form_data['conta_contabil_uuid']

    # Salva as alterações no banco de dados
    cash_flow_table.save()

def create_new_flows(form_data, iniciar_desde_o_atual=False):
    if 'due_date' not in form_data or form_data['due_date'] is None:
        return JsonResponse({'error': 'Data de due_date é necessária.'}, status=400)

    initial_installment = form_data.get('parcela_atual', 1)
    total_installments = form_data['parcelas_total']

    # Verifica se 'due_date' já é um object datetime.datetime
    if isinstance(form_data['due_date'], datetime):
        base_due_date = form_data['due_date'].date()
    else:
        # Converte de string para datetime.datetime se 'due_date' for uma string
        base_due_date = datetime.strptime(form_data['due_date'], '%Y-%m-%d').date()

    for i in range(initial_installment, total_installments + 1):
        installment_due_date = base_due_date + relativedelta(months=i - initial_installment)
        CashFlowEntry.objects.create(
            due_date=installment_due_date,
            descricao=form_data['descricao'],
            observacao=form_data['observacao'],
            valor=form_data['valor'],
            conta_contabil=form_data['conta_contabil_nome'],
            uuid_conta_contabil=form_data['conta_contabil_uuid'],
            parcela_atual=i,
            parcelas_total=total_installments,
            tags=form_data['tags'],
            natureza=form_data['natureza'],
            data_criacao=datetime.now()
        )

@csrf_exempt
def delete_entries(request):
    if request.method == 'POST':
        ids_to_delete = extract_ids_to_delete(request)

        # Verifica se algum dos lançamentos selecionados tem uuid_correlacao não nulo
        entries_with_dependencies = CashFlowEntry.objects.filter(id__in=ids_to_delete, uuid_correlacao__isnull=False)

        if entries_with_dependencies.exists():
            # Retorna uma mensagem de erro se algum lançamento tem dependência
            return JsonResponse({'status': 'error', 'message': 'Este lançamento tem dependências liquidadas.'}, status=400)
        
        # Procede com a exclusão se todos os lançamentos puderem ser excluídos
        process_ids(ids_to_delete)
        return JsonResponse({'status': 'success'})

def extract_ids_to_delete(request):
    """ Extrai os IDs do corpo da solicitação """
    data = json.loads(request.body)
    return data.get('ids', [])  # Retorna uma lista vazia se 'ids' não estiver presente

def process_ids(ids_to_delete):
    """ Processa cada ID para apagar o object correspondente e criar um registro na TabelaTemporaria """
    for id_str in ids_to_delete:
        try:
            id = int(id_str)  # Convertendo o ID para inteiro
            object = CashFlowEntry.objects.get(id=id)
            create_temporary_record(object)
            object.delete()  # Apagando o object original
        except CashFlowEntry.DoesNotExist:
            # Se o ID não for encontrado, pula para o próximo
            continue

def create_temporary_record(object):
    """ Cria um novo registro na TabelaTemporaria com base no object da CashFlowEntry """
    TabelaTemporaria.objects.create(
        due_date=object.due_date,
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
    withdrawal_bank_data = request.POST.get('banco_saida').split('|')
    deposit_bank_data = request.POST.get('banco_entrada').split('|')

    if len(withdrawal_bank_data) == 2 and len(deposit_bank_data) == 2:
        withdrawal_bank_id, withdrawal_bank_name = withdrawal_bank_data
        deposit_bank_id, deposit_bank_name = deposit_bank_data

    transfer_date = request.POST.get('data')
    transfer_transaction_amount_str = request.POST.get('valor', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    transfer_transaction_amount = Decimal(transfer_transaction_amount_str) if transfer_transaction_amount_str else 0.00
    transfer_observation = request.POST.get('observacao')
    id_correlation = uuid.uuid4()
    
    settlement_date = datetime.strptime(transfer_date, '%Y-%m-%d')

    if withdrawal_bank_id == deposit_bank_id:
        messages.error(request, "O banco de saída não pode ser igual ao banco de entrada. Por favor, selecione bancos diferentes.")
        return redirect('cash_flow')
    
    # Cria o lançamento de saída
    withdrawal_entry = SettledEntry(
        due_date=settlement_date,
        descricao=f'Transferência para {deposit_bank_name}',
        banco_id_liquidacao=withdrawal_bank_id,
        banco_liquidacao=withdrawal_bank_name,
        observacao=transfer_observation,
        valor=transfer_transaction_amount,
        conta_contabil='Transferência Saída',
        parcela_atual=1,
        parcelas_total=1,
        tags='Transferência',
        natureza='Débito',
        original_data_criacao=datetime.now(),
        data_liquidacao=settlement_date,
        uuid_correlacao=id_correlation
    )
    withdrawal_entry.save()

    # Cria o lançamento de entrada
    deposit_entry = SettledEntry(
        due_date=settlement_date,
        descricao=f'Transferência de {withdrawal_bank_name}',
        banco_id_liquidacao=deposit_bank_id,
        banco_liquidacao=deposit_bank_name,
        observacao=transfer_observation,
        valor=transfer_transaction_amount,
        conta_contabil='Transferência Entrada',
        parcela_atual=1,
        parcelas_total=1,
        tags='Transferência',
        natureza='Crédito',
        original_data_criacao=datetime.now(),
        data_liquidacao=settlement_date,
        uuid_correlacao=id_correlation
    )
    deposit_entry.save()

    return redirect(request.path)

@csrf_exempt
def process_settlement(request):
    if request.method == 'POST':
        form_data = json.loads(request.body)
        response = {'status': 'success', 'messages': []}

        for item in form_data:
            try:
                original_record = CashFlowEntry.objects.get(id=item['id'])
                total_amount = original_record.valor
                partial_amount = Decimal(item.get('valor_parcial', 0))
                is_partial_settlement = partial_amount > 0 and partial_amount <= total_amount
                completing_settlement = partial_amount == total_amount

                uuid_correlation = original_record.uuid_correlacao
                if is_partial_settlement:
                    if not uuid_correlation:
                        # Caso seja a primeira liquidação parcial
                        uuid_correlation = uuid.uuid4()
                        original_record.uuid_correlacao = uuid_correlation
                        original_record.save()
                    if partial_amount < total_amount:
                        novo_valor = total_amount - partial_amount
                        original_record.valor = novo_valor
                        original_record.save()
                    # Se for a última liquidação parcial, o UUID já está definido

                settlement_date_aware = timezone.make_aware(datetime.strptime(item['data_liquidacao'], '%Y-%m-%d'))
                installment_number = SettledEntry.objects.filter(uuid_correlacao=uuid_correlation).count() + 1 if uuid_correlation else 1

                updated_entry_description = original_record.descricao
                if is_partial_settlement:
                    updated_entry_description += f" | Parcela ({installment_number})"

                SettledEntry.objects.create(
                    fluxo_id=original_record.id,
                    due_date=original_record.due_date,
                    descricao=updated_entry_description,
                    observacao=item['observacao'],
                    valor=partial_amount if is_partial_settlement else total_amount,
                    conta_contabil=original_record.conta_contabil,
                    uuid_conta_contabil=original_record.uuid_conta_contabil,
                    parcela_atual=original_record.parcela_atual,
                    parcelas_total=original_record.parcelas_total,
                    tags=original_record.tags,
                    natureza=original_record.natureza,
                    original_data_criacao=original_record.data_criacao,
                    data_liquidacao=settlement_date_aware,
                    banco_liquidacao=item.get('banco_liquidacao', ''),
                    banco_id_liquidacao=item.get('banco_id_liquidacao', ''),
                    uuid_correlacao=uuid_correlation,
                    uuid_correlacao_parcelas=uuid_correlation
                )

                # Remove o registro original se for uma liquidação total ou a última liquidação parcial
                if completing_settlement or not is_partial_settlement:
                    original_record.delete()

            except CashFlowEntry.DoesNotExist:
                response['messages'].append(f'Registro {item["id"]} não encontrado.')
                continue

        return JsonResponse(response)
    else:
        return JsonResponse({'status': 'method not allowed'}, status=405)


# SIGNAL HANDLERS ############################################################################

@receiver(post_save, sender=CashFlowEntry)
def save_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

@receiver(post_delete, sender=CashFlowEntry)
def delete_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

def recalculate_totals():
    """ Sinal para atualizar Totais_mes_fluxo quando um FluxoDeCaixa for salvo """
    # Apaga todos os registros existentes em Totais_mes_fluxo
    Totais_mes_fluxo.objects.all().delete()

    # Encontra todas as datas únicas de due_date em CashFlowEntry
    unique_dates = CashFlowEntry.objects.dates('due_date', 'month', order='ASC')

    for unique_date in unique_dates:
        start_of_month = unique_date
        end_of_month = start_of_month + relativedelta(months=1, days=-1)

        # Calcula os totais de crédito e débito para cada mês
        total_credit = CashFlowEntry.objects.filter(
            due_date__range=(start_of_month, end_of_month),
            natureza='Crédito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        total_debit = CashFlowEntry.objects.filter(
            due_date__range=(start_of_month, end_of_month),
            natureza='Débito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        # Cria um novo registro em Totais_mes_fluxo para cada mês
        Totais_mes_fluxo.objects.create(
            data_formatada=start_of_month.strftime('%b/%Y'),
            inicio_mes=start_of_month,
            fim_mes=end_of_month,
            total_credito=total_credit,
            total_debito=total_debit,
            saldo_mensal=total_credit - total_debit
        )

# FUNÇÕES ÚNICAS ############################################################################

def filter_months(request):
    months_list = Totais_mes_fluxo.objects.all().order_by('data_formatada')
    context = {'totais_mes_fluxo': months_list}
    return render(request, 'cash_flow.html', context)

def display_banks(request):
    banks = Bancos.objects.all()
    return render(request, 'cash_flow.html', {'Banks_list': banks})
