import json
from datetime import datetime
from itertools import groupby
from django.db.models import Sum
from collections import OrderedDict
from django.shortcuts import render
from django.dispatch import receiver
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from chart_of_accounts.models import Chart_of_accounts
from cash_flow.models import CashFlowEntry, Banks, Inventory
from .models import SettledEntry, MonthsListSettled
from django.db.models.signals import post_save, post_delete

def settled_entry(request):
    if request.method == "GET":
        return display_settled(request)

def display_settled(request):
    active_banks = Banks.objects.filter(bank_status=True)
    settled_table_list = SettledEntry.objects.all().order_by('settlement_date', '-amount', 'description')
    months_list_settled = MonthsListSettled.objects.all().order_by('-end_of_month')
    chart_of_accounts_queryset = Chart_of_accounts.objects.all().order_by('-subgroup', 'account')

    accounts_by_subgroup = OrderedDict()
    for account in chart_of_accounts_queryset:
        if account.subgroup not in accounts_by_subgroup:
            accounts_by_subgroup[account.subgroup] = []
        accounts_by_subgroup[account.subgroup].append(account)

    # Convertendo QuerySet para lista para manipulação
    settled_table_list = list(settled_table_list)

    # Preparando a lista para incluir totais de cada mês
    entries_with_totals = []

    for key, group in groupby(settled_table_list, key=lambda x: x.settlement_date.strftime('%Y-%m')):
        group_list = list(group)
        entries_with_totals.extend(group_list)

        total_debit = sum(item.amount for item in group_list if item.transaction_type == 'Débito')
        total_credit = sum(item.amount for item in group_list if item.transaction_type == 'Crédito')
        total_balance = total_credit - total_debit  # Cálculo do saldo total

        # Inserir o total do mês, incluindo agora o saldo
        entries_with_totals.append({
            'settlement_date': datetime.strptime(key + "-01", '%Y-%m-%d'),
            'description': 'Total do Mês',
            'debito': total_debit,
            'credito': total_credit,
            'saldo': total_balance,  # Incluindo o saldo no dicionário
            'is_total': True,
        })

    context = {
        'Settled_table_list': entries_with_totals,
        'Months_list_settled': months_list_settled,  # Incluindo MonthsListSettled no contexto
        'Banks_list': active_banks,
        'Accounts_by_subgroup_list': accounts_by_subgroup,  # Passando o OrderedDict para o contexto
    }
    return render(request, 'settled_entry.html', context)


def display_banks(request):
    banks = Banks.objects.all()
    return render(request, 'settled_entry.html', {'Banks_list': banks})


@receiver(post_save, sender=SettledEntry)
def save_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

@receiver(post_delete, sender=SettledEntry)
def delete_update_single_date(sender, instance, **kwargs):
    recalculate_totals()

def recalculate_totals():
    # Apaga todos os entries existentes em MonthsListSettled
    MonthsListSettled.objects.all().delete()

    # Encontra todas as datas únicas de due_date em SettledEntry
    unique_dates = SettledEntry.objects.dates('settlement_date', 'month', order='ASC')

    for unique_date in unique_dates:
        start_of_month = unique_date
        end_of_month = start_of_month + relativedelta(months=1, days=-1)

        # Calcula os totais de crédito e débito para cada mês
        total_credit = SettledEntry.objects.filter(
            due_date__range=(start_of_month, end_of_month),
            transaction_type='Crédito'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_debit = SettledEntry.objects.filter(
            due_date__range=(start_of_month, end_of_month),
            transaction_type='Débito'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Cria um novo entry em MonthsListSettled para cada mês
        MonthsListSettled.objects.create(
            formatted_date=start_of_month.strftime('%b/%Y'),
            start_of_month=start_of_month,
            end_of_month=end_of_month,
            total_credit=total_credit,
            total_debit=total_debit,
            monthly_balance=total_credit - total_debit
        )

def filter_months_settled(request):
    months_list_settled = MonthsListSettled.objects.all().order_by('formatted_date')
    context = {'Months_list_settled': months_list_settled}
    return render(request, 'settled_entry.html', context)


@csrf_exempt
def process_return(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'method not allowed'}, status=405)

    data = json.loads(request.body)
    selected_ids = [item['id'] for item in data]

    for item in data:
        original_entry = SettledEntry.objects.filter(id=item['id']).first()
        if not original_entry:
            continue

        uuid_transference = original_entry.uuid_transference
        uuid_partial_settlement_correlation = original_entry.uuid_partial_settlement_correlation

        if not uuid_transference and not uuid_partial_settlement_correlation:
            create_cash_flow_entry(original_entry)
            update_inventory_quantity_on_return(
                original_entry.uuid_inventory_item,
                original_entry.inventory_quantity,
                original_entry.transaction_type
            )
        elif uuid_transference and uuid_partial_settlement_correlation is None:
            SettledEntry.objects.filter(uuid_transference=uuid_transference).delete()
        else:
            process_selected_uuids(uuid_transference, uuid_partial_settlement_correlation, selected_ids, original_entry)

    return JsonResponse({'status': 'success'})

def create_cash_flow_entry(entry):
    CashFlowEntry.objects.create(
        due_date=entry.due_date,
        description=entry.description,
        observation=entry.observation,
        amount=entry.amount,
        general_ledger_account=entry.general_ledger_account,
        current_installment=entry.current_installment,
        total_installments=entry.total_installments,
        tags=entry.tags,
        transaction_type=entry.transaction_type,
        document_type=entry.document_type,
        department=entry.department,
        department_percentage=entry.department_percentage,
        project=entry.project,
        notes=entry.notes,
        periods=entry.periods,
        weekend_action=entry.weekend_action,
        creation_date=entry.original_creation_date,
        uuid_installments_correlation=entry.uuid_installments_correlation,
        uuid_general_ledger_account=entry.uuid_general_ledger_account,
        uuid_document_type=entry.uuid_document_type,
        uuid_department=entry.uuid_department,
        uuid_project=entry.uuid_project,
        uuid_transference=entry.uuid_transference,
        inventory_item_code=entry.inventory_item_code,
        inventory_item=entry.inventory_item,
        inventory_quantity=entry.inventory_quantity,
        uuid_inventory_item=entry.uuid_inventory_item
    )
    entry.delete()

def process_selected_uuids(uuid_transference, uuid_partial_settlement_correlation, selected_ids, original_entry):
    partial_settlement_correlations = SettledEntry.objects.filter(id__in=selected_ids).values_list('uuid_partial_settlement_correlation', flat=True).distinct()

    for correlation in partial_settlement_correlations:
        if correlation is None:
            selected_entries = SettledEntry.objects.filter(id__in=selected_ids, uuid_partial_settlement_correlation__isnull=True)
            for entry in selected_entries:
                update_inventory_quantity_on_return(
                    entry.uuid_inventory_item,
                    entry.inventory_quantity,
                    entry.transaction_type
                )
                create_cash_flow_entry(entry)
            selected_entries.delete()
            continue

        more_entries = SettledEntry.objects.filter(uuid_partial_settlement_correlation=correlation).exclude(id__in=selected_ids).exists()
        exists_in_cash_flow = CashFlowEntry.objects.filter(uuid_partial_settlement_correlation=correlation).exists()

        selected_entries = SettledEntry.objects.filter(id__in=selected_ids, uuid_partial_settlement_correlation=correlation)
        selected_total_amount = selected_entries.aggregate(Sum('amount'))['amount__sum'] or 0

        # Adiciona lógica para verificar e passar dados de inventário para o próximo lançamento
        selected_with_inventory_data = selected_entries.filter(
            inventory_item_code__isnull=False,
            inventory_item__isnull=False,
            inventory_quantity__isnull=False,
            uuid_inventory_item__isnull=False
        )

        if more_entries:
            for entry in selected_with_inventory_data:
                next_entry = SettledEntry.objects.filter(
                    uuid_partial_settlement_correlation=correlation
                ).exclude(id__in=selected_ids).first()

                if next_entry:
                    next_entry.inventory_item_code = entry.inventory_item_code
                    next_entry.inventory_item = entry.inventory_item
                    next_entry.inventory_quantity = entry.inventory_quantity
                    next_entry.uuid_inventory_item = entry.uuid_inventory_item
                    next_entry.save()

        if not more_entries:
            # Se não houver mais lançamentos, atualiza o inventário no CashFlowEntry
            cash_flow_entries = CashFlowEntry.objects.filter(uuid_partial_settlement_correlation=correlation)
            if cash_flow_entries.exists():
                cash_flow_entry = cash_flow_entries.first()
                if original_entry.inventory_item_code:
                    cash_flow_entry.inventory_item_code = original_entry.inventory_item_code
                    cash_flow_entry.inventory_item = original_entry.inventory_item
                    cash_flow_entry.inventory_quantity = original_entry.inventory_quantity
                    cash_flow_entry.uuid_inventory_item = original_entry.uuid_inventory_item
                cash_flow_entry.save()
            update_inventory_quantity_on_return(
                original_entry.uuid_inventory_item,
                original_entry.inventory_quantity,
                original_entry.transaction_type
            )

        if more_entries and exists_in_cash_flow:
            unify_entries_in_cash_flow(correlation, selected_total_amount)
        elif not more_entries and exists_in_cash_flow:
            unify_entries_in_cash_flow(correlation, selected_total_amount, delete_uuid=True)
        elif not more_entries and not exists_in_cash_flow:
            create_unified_entries_in_cash_flow(selected_entries.first(), selected_total_amount, keep_uuid=False)
        elif more_entries and not exists_in_cash_flow:
            create_unified_entries_in_cash_flow(selected_entries.first(), selected_total_amount, keep_uuid=True)

        selected_entries.delete()

def unify_entries_in_cash_flow(uuid_partial_settlement_correlation, total_amount, delete_uuid=False):
    cash_flow = CashFlowEntry.objects.get(uuid_partial_settlement_correlation=uuid_partial_settlement_correlation)
    cash_flow.amount += total_amount
    if delete_uuid:
        cash_flow.uuid_partial_settlement_correlation = None
    cash_flow.save()

def create_unified_entries_in_cash_flow(entry, total_amount, keep_uuid=False):
    CashFlowEntry.objects.create(
        due_date=entry.due_date,
        description=entry.description,
        observation=entry.observation,
        amount=total_amount,
        general_ledger_account=entry.general_ledger_account,
        current_installment=entry.current_installment,
        total_installments=entry.total_installments,
        tags=entry.tags,
        transaction_type=entry.transaction_type,
        document_type=entry.document_type,
        department=entry.department,
        department_percentage=entry.department_percentage,
        project=entry.project,
        notes=entry.notes,
        periods=entry.periods,
        weekend_action=entry.weekend_action,
        creation_date=entry.original_creation_date,
        uuid_installments_correlation=entry.uuid_installments_correlation,
        uuid_general_ledger_account=entry.uuid_general_ledger_account,
        uuid_document_type=entry.uuid_document_type,
        uuid_department=entry.uuid_department,
        uuid_project=entry.uuid_project,
        uuid_transference=entry.uuid_transference,
        inventory_item_code=entry.inventory_item_code,
        inventory_item=entry.inventory_item,
        inventory_quantity=entry.inventory_quantity,
        uuid_inventory_item=entry.uuid_inventory_item,
        uuid_partial_settlement_correlation=entry.uuid_partial_settlement_correlation if keep_uuid else None
    )

def update_inventory_quantity_on_return(uuid_inventory_item, quantity_change, transaction_type):
    """Atualiza a quantidade de inventário quando um lançamento é retornado."""
    if uuid_inventory_item:
        inventory_item = Inventory.objects.get(uuid_inventory_item=uuid_inventory_item)
        if transaction_type == 'Crédito':
            inventory_item.inventory_quantity += quantity_change
        elif transaction_type == 'Débito':
            inventory_item.inventory_quantity -= quantity_change
        inventory_item.save()

@receiver(post_delete, sender=SettledEntry)
def update_bank_balance(sender, instance, **kwargs):
    try:
        bank_table_item = Banks.objects.get(id=instance.settlement_bank_id)  # Modificado para usar ID
        if instance.transaction_type == 'Crédito':
            bank_table_item.current_balance -= instance.amount  # Subtrai para créditos
        else:  # Débito
            bank_table_item.current_balance += instance.amount  # Adiciona para débitos
        bank_table_item.save()
    except Banks.DoesNotExist:
        pass  # Tratar o caso em que o bank_table_item não é encontrado, se necessário

@csrf_exempt
def update_entry(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            settled_entry = SettledEntry.objects.get(pk=id)
            
            # Assume que 'due_date' é a chave no JSON que contém a data no formato 'YYYY-MM-DD'
            due_date = data.get('due_date', None)
            if due_date:
                # Converte a data recebida para datetime, adicionando uma hora padrão se necessário
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                # Mantém a hora original da settlement_date ou define uma hora padrão (ex: meio-dia)
                original_date_time = settled_entry.settlement_date.time() if settled_entry.settlement_date else datetime.time(12, 0)
                settled_entry.settlement_date = datetime.combine(due_date, original_date_time)
            
            settled_entry.description = data.get('description', settled_entry.description)
            settled_entry.observation = data.get('observation', settled_entry.observation)

            settled_entry._skip_update_balance = True
            
            settled_entry.save()
            
            return JsonResponse({"message": "Lançamento atualizado com sucesso!"}, status=200)
        except SettledEntry.DoesNotExist:
            return JsonResponse({"error": "Lançamento não encontrado"}, status=404)
        except ValueError as e:
            # Captura erros na conversão da data
            return JsonResponse({"error": f"Erro ao processar a data: {str(e)}"}, status=400)

    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def update_entries_by_uuid(request, uuid_transference):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            due_date = data.get('novaData', None)
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                settled_entries = SettledEntry.objects.filter(uuid_transference=uuid_transference)
                for settled_entry in settled_entries:
                    original_date_time = settled_entry.settlement_date.time() if settled_entry.settlement_date else datetime.time(12, 0)
                    settled_entry.settlement_date = datetime.combine(due_date, original_date_time)
                    settled_entry._skip_update_balance = True
                    settled_entry.save()
            
            return JsonResponse({"message": f"Lançamentos atualizados com sucesso para o UUID {uuid_transference}!"}, status=200)
        except ValueError as e:
            return JsonResponse({"error": f"Erro ao processar a data: {str(e)}"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)