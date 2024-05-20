import uuid
import json
from decimal import Decimal
from datetime import datetime, timedelta
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
from .models import CashFlowEntry, TemporaryTable, MonthsListCashFlow, Banks, DocumentType, Departments

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
    document_type_cash_flow = DocumentType.objects.all()
    departments_cash_flow = Departments.objects.all()

    accounts_by_subgroup = group_accounts_by_subgroup(accounts_queryset)
    entries_with_totals = calculate_monthly_totals(cash_flow_entries)

    context = {
        'Cash_flow_table_list': entries_with_totals,
        'Months_list_cash_flow': months_list_cash_flow,
        'Banks_list': active_banks,
        'Accounts_by_subgroup_list': accounts_by_subgroup,
        'Document_types': document_type_cash_flow,
        'Departments': departments_cash_flow,
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
    if 'transferences' in request.POST and request.POST['transferences'] == 'process_transfer':
        return process_transfer(request)
    else:
        form_data = get_form_data(request)
    if form_data['entry_id']:
        if form_data['total_installments'] > 1:
            if form_data['original_total_installments'] > 1:
                update_existing_cash_flow_entries(form_data)  # Manter total_installments se for uma série de installments
            else:
                # Criar novos fluxos se o número de installments foi alterado para mais de um
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
    due_date = get_due_date(request)
    transaction_amount = get_transaction_amount(request)
    account_data = get_account_data(request, transaction_type)
    other_data = get_other_data(request)
    entry_id = get_entry_id(request, transaction_type)
    uuid_partial_settlement_correlation = get_uuid_partial_settlement_correlation(request, transaction_type)
    document_type_data = get_document_type_data(request, transaction_type)
    periods_data = get_periods_data(request, transaction_type)
    weekend_action = get_weekend_action_data(request, transaction_type)
    department_data = get_department_data(request, transaction_type)

    return {
        'due_date': due_date,
        'description': other_data['entry_description'],
        'observation': other_data['entry_observation'],
        'amount': transaction_amount,
        'general_ledger_account_name': account_data['account_name'],
        'general_ledger_account_uuid': account_data['account_uuid'],
        'total_installments': other_data['total_installments'],
        'original_total_installments': other_data['original_total_installments'],
        'tags': other_data['entry_tags'],
        'notes': other_data['entry_notes'],
        'entry_id': entry_id,
        'uuid_partial_settlement_correlation': uuid_partial_settlement_correlation,
        'transaction_type': transaction_type,
        'document_type_name': document_type_data['document_type_name'],
        'document_type_uuid': document_type_data['document_type_uuid'],
        'periods': periods_data,
        'weekend_action': weekend_action,
        'department_name': department_data['department_name'],
        'department_percentage': department_data['department_percentage'],
        'department_uuid': department_data['department_uuid'],
    }

def get_transaction_type(request):
    return 'Crédito' if 'modal_save_credit' in request.POST else 'Débito'

def get_account_data(request, transaction_type):
    account_name_field = 'general_ledger_account_name_credit' if transaction_type == 'Crédito' else 'general_ledger_account_name_debit'
    account_uuid_field = 'general_ledger_account_uuid_credit' if transaction_type == 'Crédito' else 'general_ledger_account_uuid_debit'
    account_name = request.POST.get(account_name_field)
    account_uuid = request.POST.get(account_uuid_field)
    return {'account_uuid': account_uuid, 'account_name': account_name}

def get_entry_id(request, transaction_type):
    receipt_entry_id = request.POST.get('entry_id_credit')
    payment_entry_id = request.POST.get('entry_id_debit')

    if transaction_type == 'Crédito' and receipt_entry_id:
        return int(receipt_entry_id)
    elif transaction_type == 'Débito' and payment_entry_id:
        return int(payment_entry_id)
    return None

def get_uuid_partial_settlement_correlation(request, transaction_type):
    uuid_partial_settlement_correlation_field = 'uuid_partial_settlement_correlation_credit' if transaction_type == 'Crédito' else 'uuid_partial_settlement_correlation_debit'
    uuid_partial_settlement_correlation = request.POST.get(uuid_partial_settlement_correlation_field)
    
    # Verifica se o valor recebido é a string 'None'
    if uuid_partial_settlement_correlation == 'None':
        return {'uuid_partial_settlement_correlation': None}
    else:
        return {'uuid_partial_settlement_correlation': uuid_partial_settlement_correlation}

def get_due_date(request):
    due_date_str = request.POST.get('due_date')
    return datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

def get_transaction_amount(request):
    transaction_amount_str = request.POST.get('amount', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    return float(transaction_amount_str) if transaction_amount_str else 0.00

def get_other_data(request):
    entry_description = request.POST.get('description', '')
    entry_observation = request.POST.get('observation', '')
    entry_notes = request.POST.get('notes', '')
    installment = request.POST.get('installments', '1')
    total_installments = int(installment) if installment.isdigit() else 1
    original_total_installments = int(request.POST.get('original_total_installments', '1'))
    entry_tags = request.POST.get('tags', '')
    return {
        'entry_description': entry_description,
        'entry_observation': entry_observation,
        'total_installments': total_installments,
        'original_total_installments': original_total_installments,
        'entry_notes': entry_notes,
        'entry_tags': entry_tags,
    }

def get_document_type_data(request, transaction_type):
    document_type_name_field = 'document_type_name_credit' if transaction_type == 'Crédito' else 'document_type_name_debit'
    document_type_uuid_field = 'document_type_uuid_credit' if transaction_type == 'Crédito' else 'document_type_uuid_debit'

    document_type_name = request.POST.get(document_type_name_field)
    document_type_uuid = request.POST.get(document_type_uuid_field)

    # Substituir strings vazias por None
    if document_type_name == '':
        document_type_name = None
    if document_type_uuid == '':
        document_type_uuid = None

    return {'document_type_name': document_type_name, 'document_type_uuid': document_type_uuid}

def get_weekend_action_data(request, transaction_type):
    weekend_action_field = 'weekend_action_credit' if transaction_type == 'Crédito' else 'weekend_action_debit'
    weekend_action = request.POST.get(weekend_action_field)
    return weekend_action

def get_periods_data(request, transaction_type):
    recurrence = request.POST.get('recurrence')
    periods_field = 'periods_credit' if transaction_type == 'Crédito' else 'periods_debit'
    if recurrence == 'no':
        return 'monthly'
    else:
        # Caso contrário, usa o valor enviado pelo formulário
        periods = request.POST.get(periods_field)
        return periods if periods else 'monthly'

def get_department_data(request, transaction_type):
    department_name_field = 'department_name_credit' if transaction_type == 'Crédito' else 'department_name_debit'
    department_uuid_field = 'department_uuid_credit' if transaction_type == 'Crédito' else 'department_uuid_debit'
    department_percentage_field = 'department_percentage_credit' if transaction_type == 'Crédito' else 'department_percentage_debit'
    department_name = request.POST.get(department_name_field, '[]')
    department_uuid = request.POST.get(department_uuid_field, '[]')
    department_percentage = request.POST.get(department_percentage_field, '[]')

    try:
        department_name_list = json.loads(department_name)
        department_uuid_list = json.loads(department_uuid)
        department_percentage_list = json.loads(department_percentage)
    except json.JSONDecodeError:
        department_name_list = []
        department_uuid_list = []
        department_percentage_list = []

    return {
        'department_name': department_name_list,
        'department_uuid': department_uuid_list,
        'department_percentage': department_percentage_list
    }

def update_existing_cash_flow_entries(form_data):
    # Busca o fluxo de caixa pelo ID
    cash_flow_table = get_object_or_404(CashFlowEntry, id=form_data['entry_id'])
    
    # Atualiza campos comuns diretamente
    cash_flow_table.transaction_type = form_data['transaction_type']
    cash_flow_table.due_date = form_data['due_date']
    cash_flow_table.description = form_data['description']
    cash_flow_table.observation = form_data['observation']
    cash_flow_table.amount = form_data['amount']
    cash_flow_table.notes = form_data['notes']
    
    # Atualiza a conta contábil e seu UUID
    cash_flow_table.general_ledger_account = form_data['general_ledger_account_name']
    cash_flow_table.uuid_general_ledger_account = form_data['general_ledger_account_uuid']

    # Atualiza o tipo de documento e seu UUID
    cash_flow_table.document_type = form_data['document_type_name']
    cash_flow_table.uuid_document_type = form_data['document_type_uuid']

    # Atualiza os períodos
    cash_flow_table.periods = form_data['periods']

    # Atualiza o tipo de department e seu UUID
    cash_flow_table.department = form_data['department_name']
    cash_flow_table.uuid_department = form_data['department_uuid']
    cash_flow_table.department_percentage = form_data['department_percentage']

    # Não altera total_installments se já é parte de uma série de installments
    if cash_flow_table.total_installments <= 1 or 'total_installments' not in form_data:
        cash_flow_table.total_installments = form_data.get('total_installments', cash_flow_table.total_installments)
    
    cash_flow_table.tags = form_data['tags']

    # Salva as alterações no banco de dados
    cash_flow_table.save()

def create_cash_flow_entries(form_data):
    if 'due_date' not in form_data or form_data['due_date'] is None:
        return JsonResponse({'error': 'Data de vencimento é necessária.'}, status=400)

    initial_installment = form_data.get('current_installment', 1)
    total_installments = form_data['total_installments']
    uuid_installments_correlation = None

    # Converte 'due_date' para datetime.date se necessário
    if isinstance(form_data['due_date'], datetime):
        base_due_date = form_data['due_date'].date()
    else:
        base_due_date = datetime.strptime(form_data['due_date'], '%Y-%m-%d').date()

    if total_installments > 1:
        uuid_installments_correlation = uuid.uuid4()

    for i in range(initial_installment, total_installments + 1):
        if form_data['periods'] == 'weekly':
            installment_due_date = base_due_date + relativedelta(weeks=i - initial_installment)
        elif form_data['periods'] == 'bimonthly':
            installment_due_date = base_due_date + relativedelta(months=2 * (i - initial_installment))
        elif form_data['periods'] == 'semiannual':
            installment_due_date = base_due_date + relativedelta(months=6 * (i - initial_installment))
        elif form_data['periods'] == 'yearly':
            installment_due_date = base_due_date + relativedelta(years=i - initial_installment)
        else:  # Default to monthly
            installment_due_date = base_due_date + relativedelta(months=i - initial_installment)

        # Ajusta a data com base na ação de final de semana
        installment_due_date = adjust_date_for_weekend(installment_due_date, form_data['weekend_action'])

        CashFlowEntry.objects.create(
            due_date=installment_due_date,
            description=form_data['description'],
            observation=form_data['observation'],
            amount=form_data['amount'],
            general_ledger_account=form_data['general_ledger_account_name'],
            uuid_general_ledger_account=form_data['general_ledger_account_uuid'],
            document_type=form_data['document_type_name'],
            uuid_document_type=form_data['document_type_uuid'],
            department=form_data['department_name'],
            department_percentage=form_data['department_percentage'],
            uuid_department=form_data['department_uuid'],
            current_installment=i,
            total_installments=total_installments,
            notes=form_data['notes'],
            tags=form_data['tags'],
            periods=form_data['periods'],
            transaction_type=form_data['transaction_type'],
            weekend_action=form_data['weekend_action'],
            uuid_installments_correlation=uuid_installments_correlation,
            creation_date=datetime.now(),
        )

def adjust_date_for_weekend(due_date, weekend_action):
    if weekend_action == 'postpone':
        while due_date.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
            due_date += timedelta(days=1)
    elif weekend_action == 'antedate':
        while due_date.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
            due_date -= timedelta(days=1)
    return due_date

@csrf_exempt
def delete_entries(request):
    if request.method == 'POST':
        ids_to_delete = extract_ids_to_delete(request)

        # Verifica se algum dos lançamentos selecionados tem uuid_partial_settlement_correlation não nulo
        entries_with_dependencies = CashFlowEntry.objects.filter(id__in=ids_to_delete, uuid_partial_settlement_correlation__isnull=False)

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

    transfer_date = request.POST.get('transfer_date')
    transfer_transaction_amount_str = request.POST.get('amount', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    transfer_transaction_amount = Decimal(transfer_transaction_amount_str) if transfer_transaction_amount_str else 0.00
    transfer_observation = request.POST.get('observation')
    uuid_transference = uuid.uuid4()
    
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
        uuid_transference=uuid_transference
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
        uuid_transference=uuid_transference
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
        uuid_partial_settlement_correlation = update_uuid_partial_settlement_correlation(original_record, partial_amount, is_partial_settlement)
        create_settled_entry(item, original_record, partial_amount, is_partial_settlement, uuid_partial_settlement_correlation)
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

def update_uuid_partial_settlement_correlation(original_record, partial_amount, is_partial_settlement):
    if is_partial_settlement and not original_record.uuid_partial_settlement_correlation:
        original_record.uuid_partial_settlement_correlation = uuid.uuid4()
        original_record.save()
    return original_record.uuid_partial_settlement_correlation

def create_settled_entry(item, original_record, partial_amount, is_partial_settlement, uuid_partial_settlement_correlation):
    settlement_date_aware = timezone.make_aware(datetime.strptime(item['settlement_date'], '%Y-%m-%d'))
    installment_number = SettledEntry.objects.filter(uuid_partial_settlement_correlation=uuid_partial_settlement_correlation).count() + 1 if uuid_partial_settlement_correlation else 1
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
        uuid_partial_settlement_correlation=uuid_partial_settlement_correlation
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
