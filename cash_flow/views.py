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
from typing import Dict, List, Tuple
from realizado.models import SettledEntry
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from chart_of_accounts.models import Chart_of_accounts
from django.db.models.signals import post_save, post_delete
from django.shortcuts import render, redirect, get_object_or_404
from .models import CashFlowEntry, TemporaryTable, MonthsListCashFlow, Banks

def cash_flow(request):
    if request.method == "GET":
        return display_cash_flow(request)
    elif request.method == "POST":
        return process_cash_flow_form(request)

def display_cash_flow(request):
    active_banks = Banks.objects.filter(bank_status=True)
    cash_flow_entries = CashFlowEntry.objects.all().order_by('due_date', '-amount', 'description')
    months_list_cash_flow = MonthsListCashFlow.objects.all()
    accounts_queryset = Chart_of_accounts.objects.all().order_by('-subgroup', 'account')

    accounts_by_subgroup = group_accounts_by_subgroup(accounts_queryset)
    entries_with_totals = calculate_monthly_totals(cash_flow_entries)

    context = {
        'Cash_flow_table_list': entries_with_totals,
        'Months_list_cash_flow': months_list_cash_flow,
        'Banks_list': active_banks,
        'Accounts_by_subgroup_list': accounts_by_subgroup,
    }
    return render(request, 'cash_flow.html', context)

def group_accounts_by_subgroup(accounts_queryset) -> OrderedDict:
    """ Groups accounts by their subgroup and returns an OrderedDict. """
    accounts_by_subgroup = OrderedDict()
    for account in accounts_queryset:
        subgroup = account.subgroup
        accounts_by_subgroup.setdefault(subgroup, []).append(account)
    return accounts_by_subgroup

def calculate_monthly_totals(cash_flow_entries) -> List[Dict]:
    """ Calculates monthly totals for cash flow entries and returns a list of dictionaries. """
    entries_with_totals = []
    for key, group in groupby(cash_flow_entries, key=lambda x: x.due_date.strftime('%Y-%m')):
        group_list = list(group)
        entries_with_totals.extend(group_list)

        total_debit = sum(entry.amount for entry in group_list if entry.transaction_type == 'Débito')
        total_credit = sum(entry.amount for entry in group_list if entry.transaction_type == 'Crédito')
        total_balance = total_credit - total_debit

        entries_with_totals.append({
            'due_date': datetime.strptime(key + "-01", '%Y-%m-%d'),
            'description': 'Total do Mês',
            'debito': total_debit,
            'credito': total_credit,
            'saldo': total_balance,
            'is_total': True,
        })

    return entries_with_totals

def process_cash_flow_form(request):
    if 'transferencias' in request.POST and request.POST['transferencias'] == 'transferencia':
        return process_transfer(request)
    else:
        form_data = get_form_data(request)
    if form_data['entry_id']:
        if form_data['total_installments'] > 1:
            if form_data['total_installments_originais'] > 1:
                update_existing_cash_flow_entries(form_data)  # Manter total_installments se for uma série de parcelas
            else:
                # Criar novos fluxos se o número de parcelas foi alterado para mais de um
                CashFlowEntry.objects.filter(id=form_data['entry_id']).delete()
                create_cash_flow_entries(form_data)
        else:
            update_existing_cash_flow_entries(form_data)
    else:
        create_cash_flow_entries(form_data)
    return redirect(request.path)

def get_form_data(request):
    """Extracts and returns form data from the request."""
    transaction_type = get_transaction_type(request)
    account_data = get_account_data(request, transaction_type)
    entry_id = get_entry_id(request, transaction_type)
    due_date = get_due_date(request)
    transaction_amount = get_transaction_amount(request)
    other_data = get_other_data(request)

    return {
        'due_date': due_date,
        'description': other_data['entry_description'],
        'observation': other_data['entry_observation'],
        'amount': transaction_amount,
        'general_ledger_account_uuid': account_data['account_uuid'],
        'general_ledger_account_nome': account_data['account_name'],
        'total_installments': other_data['total_installments'],
        'total_installments_originais': other_data['original_total_installments'],
        'tags': other_data['entry_tags'],
        'entry_id': entry_id,
        'transaction_type': transaction_type,
    }

def get_transaction_type(request):
    return 'Crédito' if 'salvar_credit' in request.POST else 'Débito'

def get_account_data(request, transaction_type):
    account_uuid_field = 'general_ledger_account_uuid_credits' if transaction_type == 'Crédito' else 'general_ledger_account_uuid_debits'
    account_name_field = 'general_ledger_account_nome_credits' if transaction_type == 'Crédito' else 'general_ledger_account_nome_debits'
    account_uuid = request.POST.get(account_uuid_field)
    account_name = request.POST.get(account_name_field)
    return {'account_uuid': account_uuid, 'account_name': account_name}

def get_entry_id(request, transaction_type):
    receipt_entry_id = request.POST.get('entry_id_credits')
    payment_entry_id = request.POST.get('entry_id_debits')

    if transaction_type == 'Crédito' and receipt_entry_id:
        return int(receipt_entry_id)
    elif transaction_type == 'Débito' and payment_entry_id:
        return int(payment_entry_id)
    return None

def get_due_date(request):
    due_date_str = request.POST.get('due_date')
    return datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

def get_transaction_amount(request):
    transaction_amount_str = request.POST.get('amount', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    return float(transaction_amount_str) if transaction_amount_str else 0.00

def get_other_data(request):
    entry_description = request.POST.get('description', '')
    entry_observation = request.POST.get('observation', '')
    installment = request.POST.get('parcelas', '1')
    total_installments = int(installment) if installment.isdigit() else 1
    original_total_installments = int(request.POST.get('total_installments_originais', '1'))
    entry_tags = request.POST.get('tags', '')
    return {
        'entry_description': entry_description,
        'entry_observation': entry_observation,
        'total_installments': total_installments,
        'original_total_installments': original_total_installments,
        'entry_tags': entry_tags,
    }

def update_existing_cash_flow_entries(form_data):
    # Busca o fluxo de caixa pelo ID
    cash_flow_table = get_object_or_404(CashFlowEntry, id=form_data['entry_id'])
    
    # Atualiza campos comuns diretamente
    cash_flow_table.due_date = form_data['due_date']
    cash_flow_table.description = form_data['description']
    cash_flow_table.observation = form_data['observation']
    cash_flow_table.amount = form_data['amount']
    cash_flow_table.transaction_type = form_data['transaction_type']
    # Não altera total_installments se já é parte de uma série de parcelas
    if cash_flow_table.total_installments <= 1 or 'total_installments' not in form_data:
        cash_flow_table.total_installments = form_data.get('total_installments', cash_flow_table.total_installments)
    cash_flow_table.tags = form_data['tags']

    # Atualiza a conta contábil e seu UUID
    cash_flow_table.general_ledger_account = form_data['general_ledger_account_nome']
    cash_flow_table.uuid_general_ledger_account = form_data['general_ledger_account_uuid']

    # Salva as alterações no banco de dados
    cash_flow_table.save()

def create_cash_flow_entries(form_data):
    if 'due_date' not in form_data or form_data['due_date'] is None:
        return JsonResponse({'error': 'Data de due_date é necessária.'}, status=400)

    initial_installment = form_data.get('current_installment', 1)
    total_installments = form_data['total_installments']

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
            description=form_data['description'],
            observation=form_data['observation'],
            amount=form_data['amount'],
            general_ledger_account=form_data['general_ledger_account_nome'],
            uuid_general_ledger_account=form_data['general_ledger_account_uuid'],
            current_installment=i,
            total_installments=total_installments,
            tags=form_data['tags'],
            transaction_type=form_data['transaction_type'],
            creation_date=datetime.now()
        )

@csrf_exempt
def delete_entries(request):
    if request.method == 'POST':
        ids_to_delete = extract_ids_to_delete(request)

        # Verifica se algum dos lançamentos selecionados tem uuid_correlation não nulo
        entries_with_dependencies = CashFlowEntry.objects.filter(id__in=ids_to_delete, uuid_correlation__isnull=False)

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
    """ Processa cada ID para apagar o object correspondente e criar um registro na TemporaryTable """
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
    """ Cria um novo registro na TemporaryTable com base no object da CashFlowEntry """
    TemporaryTable.objects.create(
        due_date=object.due_date,
        description=object.description,
        observation=object.observation,
        amount=object.amount,
        general_ledger_account=object.general_ledger_account,
        uuid_general_ledger_account=object.uuid_general_ledger_account,
        current_installment=object.current_installment,
        total_installments=object.total_installments,
        tags=object.tags,
        transaction_type=object.transaction_type,
        creation_date=object.creation_date
    )

def process_transfer(request):
    withdrawal_bank_data = request.POST.get('banco_saida').split('|')
    deposit_bank_data = request.POST.get('banco_entrada').split('|')

    if len(withdrawal_bank_data) == 2 and len(deposit_bank_data) == 2:
        withdrawal_bank_id, withdrawal_bank_name = withdrawal_bank_data
        deposit_bank_id, deposit_bank_name = deposit_bank_data

    transfer_date = request.POST.get('data')
    transfer_transaction_amount_str = request.POST.get('amount', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    transfer_transaction_amount = Decimal(transfer_transaction_amount_str) if transfer_transaction_amount_str else 0.00
    transfer_observation = request.POST.get('observation')
    id_correlation = uuid.uuid4()
    
    settlement_date = datetime.strptime(transfer_date, '%Y-%m-%d')

    if withdrawal_bank_id == deposit_bank_id:
        messages.error(request, "O banco de saída não pode ser igual ao banco de entrada. Por favor, selecione bancos diferentes.")
        return redirect('cash_flow')
    
    # Cria o lançamento de saída
    withdrawal_entry = SettledEntry(
        due_date=settlement_date,
        description=f'Transferência para {deposit_bank_name}',
        settlement_bank_id=withdrawal_bank_id,
        settlement_bank=withdrawal_bank_name,
        observation=transfer_observation,
        amount=transfer_transaction_amount,
        general_ledger_account='Transferência Saída',
        current_installment=1,
        total_installments=1,
        tags='Transferência',
        transaction_type='Débito',
        original_creation_date=datetime.now(),
        settlement_date=settlement_date,
        uuid_correlation=id_correlation
    )
    withdrawal_entry.save()

    # Cria o lançamento de entrada
    deposit_entry = SettledEntry(
        due_date=settlement_date,
        description=f'Transferência de {withdrawal_bank_name}',
        settlement_bank_id=deposit_bank_id,
        settlement_bank=deposit_bank_name,
        observation=transfer_observation,
        amount=transfer_transaction_amount,
        general_ledger_account='Transferência Entrada',
        current_installment=1,
        total_installments=1,
        tags='Transferência',
        transaction_type='Crédito',
        original_creation_date=datetime.now(),
        settlement_date=settlement_date,
        uuid_correlation=id_correlation
    )
    deposit_entry.save()

    return redirect(request.path)

@csrf_exempt
def process_settlement(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'method not allowed'}, status=405)
    
    form_data = json.loads(request.body)
    response = process_form_data(form_data)
    return JsonResponse(response)

def process_form_data(form_data):
    response = {'status': 'success', 'messages': []}
    for item in form_data:
        process_single_item(item, response)
    return response

def process_single_item(item, response):
    try:
        original_record = get_cash_flow_entry(item['id'])
        partial_amount, is_partial_settlement, completing_settlement = calculate_settlement_info(item, original_record)
        uuid_correlation = update_uuid_correlation(original_record, partial_amount, is_partial_settlement)
        create_settled_entry(item, original_record, partial_amount, is_partial_settlement, uuid_correlation)
        update_original_record_if_needed(original_record, partial_amount, is_partial_settlement, completing_settlement)
    except CashFlowEntry.DoesNotExist:
        response['messages'].append(f'Registro {item["id"]} não encontrado.')

def get_cash_flow_entry(entry_id):
    return CashFlowEntry.objects.get(id=entry_id)

def calculate_settlement_info(item, original_record):
    total_amount = original_record.amount
    partial_amount = Decimal(item.get('partial_amount', 0))
    is_partial_settlement = partial_amount > 0 and partial_amount <= total_amount
    completing_settlement = partial_amount == total_amount
    return partial_amount, is_partial_settlement, completing_settlement

def update_uuid_correlation(original_record, partial_amount, is_partial_settlement):
    if is_partial_settlement and not original_record.uuid_correlation:
        original_record.uuid_correlation = uuid.uuid4()
        original_record.save()
    return original_record.uuid_correlation

def create_settled_entry(item, original_record, partial_amount, is_partial_settlement, uuid_correlation):
    settlement_date_aware = timezone.make_aware(datetime.strptime(item['settlement_date'], '%Y-%m-%d'))
    installment_number = SettledEntry.objects.filter(uuid_correlation=uuid_correlation).count() + 1 if uuid_correlation else 1
    updated_entry_description = f"{original_record.description} | Parcela ({installment_number})" if is_partial_settlement else original_record.description

    SettledEntry.objects.create(
        cash_flow_id=original_record.id,
        due_date=original_record.due_date,
        description=updated_entry_description,
        observation=item['observation'],
        amount=partial_amount if is_partial_settlement else original_record.amount,
        general_ledger_account=original_record.general_ledger_account,
        uuid_general_ledger_account=original_record.uuid_general_ledger_account,
        current_installment=original_record.current_installment,
        total_installments=original_record.total_installments,
        tags=original_record.tags,
        transaction_type=original_record.transaction_type,
        original_creation_date=original_record.creation_date,
        settlement_date=settlement_date_aware,
        settlement_bank=item.get('settlement_bank', ''),
        settlement_bank_id=item.get('settlement_bank_id', ''),
        uuid_correlation=uuid_correlation,
        uuid_correlation_installments=uuid_correlation
    )

def update_original_record_if_needed(original_record, partial_amount, is_partial_settlement, completing_settlement):
    if completing_settlement or not is_partial_settlement:
        original_record.delete()
    elif partial_amount < original_record.amount:
        original_record.amount -= partial_amount
        original_record.save()


# SIGNAL HANDLERS ############################################################################

@receiver(post_save, sender=CashFlowEntry)
def save_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

@receiver(post_delete, sender=CashFlowEntry)
def delete_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

def recalculate_totals():
    """ Sinal para atualizar MonthsListCashFlow quando um FluxoDeCaixa for salvo """
    # Apaga todos os registros existentes em MonthsListCashFlow
    MonthsListCashFlow.objects.all().delete()

    # Encontra todas as datas únicas de due_date em CashFlowEntry
    unique_dates = CashFlowEntry.objects.dates('due_date', 'month', order='ASC')

    for unique_date in unique_dates:
        start_of_month = unique_date
        end_of_month = start_of_month + relativedelta(months=1, days=-1)

        # Calcula os totais de crédito e débito para cada mês
        total_credit = CashFlowEntry.objects.filter(
            due_date__range=(start_of_month, end_of_month),
            transaction_type='Crédito'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_debit = CashFlowEntry.objects.filter(
            due_date__range=(start_of_month, end_of_month),
            transaction_type='Débito'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Cria um novo registro em MonthsListCashFlow para cada mês
        MonthsListCashFlow.objects.create(
            formatted_date=start_of_month.strftime('%b/%Y'),
            start_of_month=start_of_month,
            end_of_month=end_of_month,
            total_credit=total_credit,
            total_debit=total_debit,
            monthly_balance=total_credit - total_debit
        )

# FUNÇÕES ÚNICAS ############################################################################

def filter_months_cash_flow(request):
    months_list_cash_flow = MonthsListCashFlow.objects.all().order_by('formatted_date')
    context = {'Months_list_cash_flow': months_list_cash_flow}
    return render(request, 'cash_flow.html', context)

def display_banks(request):
    banks = Banks.objects.all()
    return render(request, 'cash_flow.html', {'Banks_list': banks})
