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
from fluxo_de_caixa.models import CashFlowEntry, Bancos
from .models import SettledEntry, MonthsListSettled
from django.db.models.signals import post_save, post_delete

def realizado(request):
    if request.method == "GET":
        return exibir_realizado(request)

def exibir_realizado(request):
    bancos_ativos = Bancos.objects.filter(status=True)
    Tabela_realizado_list = SettledEntry.objects.all().order_by('data_liquidacao', '-amount', 'description')
    months_list_settled = MonthsListSettled.objects.all().order_by('-end_of_month')
    chart_of_accounts_queryset = Chart_of_accounts.objects.all().order_by('-subgroup', 'account')

    accounts_by_subgroup = OrderedDict()
    for account in chart_of_accounts_queryset:
        if account.subgroup not in accounts_by_subgroup:
            accounts_by_subgroup[account.subgroup] = []
        accounts_by_subgroup[account.subgroup].append(account)

    # Convertendo QuerySet para lista para manipulação
    Tabela_realizado_list = list(Tabela_realizado_list)

    # Preparando a lista para incluir totais de cada mês
    lancamentos_com_totais = []

    for key, group in groupby(Tabela_realizado_list, key=lambda x: x.data_liquidacao.strftime('%Y-%m')):
        lista_grupo = list(group)
        lancamentos_com_totais.extend(lista_grupo)

        total_debit = sum(item.amount for item in lista_grupo if item.transaction_type == 'Débito')
        total_credit = sum(item.amount for item in lista_grupo if item.transaction_type == 'Crédito')
        saldo_total = total_credit - total_debit  # Cálculo do saldo total

        # Inserir o total do mês, incluindo agora o saldo
        lancamentos_com_totais.append({
            'data_liquidacao': datetime.strptime(key + "-01", '%Y-%m-%d'),
            'description': 'Total do Mês',
            'debito': total_debit,
            'credito': total_credit,
            'saldo': saldo_total,  # Incluindo o saldo no dicionário
            'is_total': True,
        })

    context = {
        'Tabela_realizado_list': lancamentos_com_totais,
        'Months_List_Settled': months_list_settled,  # Incluindo MonthsListSettled no contexto
        'bancos': bancos_ativos,
        'accounts_by_subgroup': accounts_by_subgroup,  # Passando o OrderedDict para o contexto
    }
    return render(request, 'realizado.html', context)


def exibir_bancos(request):
    bancos = Bancos.objects.all()
    return render(request, 'realizado.html', {'bancos': bancos})


@receiver(post_save, sender=SettledEntry)
def save_update_data_unica_realizado(sender, instance, **kwargs):
    recalcular_totais_realizado()

@receiver(post_delete, sender=SettledEntry)
def delete_update_data_unica_realizado(sender, instance, **kwargs):
    recalcular_totais_realizado()

def recalcular_totais_realizado():
    # Apaga todos os registros existentes em MonthsListSettled
    MonthsListSettled.objects.all().delete()

    # Encontra todas as datas únicas de due_date em SettledEntry
    datas_unicas = SettledEntry.objects.dates('data_liquidacao', 'month', order='ASC')

    for data_unica in datas_unicas:
        start_of_month = data_unica
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

        # Cria um novo registro em MonthsListSettled para cada mês
        MonthsListSettled.objects.create(
            formatted_date=start_of_month.strftime('%b/%Y'),
            start_of_month=start_of_month,
            end_of_month=end_of_month,
            total_credit=total_credit,
            total_debit=total_debit,
            monthly_balance=total_credit - total_debit
        )

def meses_filtro_realizado(request):
    months_list_settled = MonthsListSettled.objects.all().order_by('formatted_date')
    context = {'Months_List_Settled': months_list_settled}
    return render(request, 'realizado.html', context)


@csrf_exempt
def processar_retorno(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'method not allowed'}, status=405)

    dados = json.loads(request.body)
    ids_selecionados = [item['id'] for item in dados]

    for item in dados:
        registro_original = SettledEntry.objects.filter(id=item['id']).first()
        if not registro_original:
            continue

        uuid_correlation = registro_original.uuid_correlation
        uuid_correlation_parcelas = registro_original.uuid_correlation_parcelas

        if not uuid_correlation:
            criar_fluxo_com_registro(registro_original)
        elif uuid_correlation and uuid_correlation_parcelas is None:
            # Aqui é onde implementamos a lógica específica: Deletar todos os lançamentos em SettledEntry que compartilham o mesmo uuid_correlation
            SettledEntry.objects.filter(uuid_correlation=uuid_correlation).delete()
        else:
            processar_lancamentos_com_uuids_selecionados(uuid_correlation, uuid_correlation_parcelas, ids_selecionados, registro_original)

    return JsonResponse({'status': 'success'})

def criar_fluxo_com_registro(registro):
    CashFlowEntry.objects.create(
        due_date=registro.due_date,
        description=registro.description,
        observation=registro.observation,
        amount=registro.amount,
        general_ledger_account=registro.general_ledger_account,
        uuid_general_ledger_account=registro.uuid_general_ledger_account,
        current_installment=registro.current_installment,
        total_installments=registro.total_installments,
        tags=registro.tags,
        transaction_type=registro.transaction_type,
        creation_date=registro.original_creation_date,
    )
    registro.delete()

def processar_lancamentos_com_uuids_selecionados(uuid_correlation, uuid_correlation_parcelas, ids_selecionados, registro_original):
    mais_registros = SettledEntry.objects.filter(uuid_correlation=uuid_correlation, uuid_correlation_parcelas=uuid_correlation_parcelas).exclude(id__in=ids_selecionados).exists()
    existe_no_fluxo = CashFlowEntry.objects.filter(uuid_correlation=uuid_correlation).exists()

    registros_selecionados = SettledEntry.objects.filter(id__in=ids_selecionados, uuid_correlation=uuid_correlation, uuid_correlation_parcelas=uuid_correlation_parcelas)
    selected_total_amount = registros_selecionados.aggregate(Sum('amount'))['amount__sum'] or 0

    if mais_registros and existe_no_fluxo:
        unificar_lancamentos_no_fluxo(uuid_correlation, selected_total_amount)
    elif not mais_registros and existe_no_fluxo:
        unificar_lancamentos_no_fluxo(uuid_correlation, selected_total_amount, excluir_uuid=True)
    elif not mais_registros and not existe_no_fluxo:
        criar_fluxo_com_registro_unificado(registros_selecionados.first(), selected_total_amount, manter_uuid=False)
    elif mais_registros and not existe_no_fluxo:
        criar_fluxo_com_registro_unificado(registros_selecionados.first(), selected_total_amount, manter_uuid=True)

    registros_selecionados.delete()

def unificar_lancamentos_no_fluxo(uuid_correlation, total_amount, excluir_uuid=False):
    fluxo = CashFlowEntry.objects.get(uuid_correlation=uuid_correlation)
    fluxo.amount += total_amount
    if excluir_uuid:
        fluxo.uuid_correlation = None
    fluxo.save()

def criar_fluxo_com_registro_unificado(registro, total_amount, manter_uuid=False):
    CashFlowEntry.objects.create(
        due_date=registro.due_date,
        description=registro.description,
        observation=registro.observation,
        amount=total_amount,
        general_ledger_account=registro.general_ledger_account,
        uuid_general_ledger_account=registro.uuid_general_ledger_account,
        current_installment=registro.current_installment,
        total_installments=registro.total_installments,
        tags=registro.tags,
        transaction_type=registro.transaction_type,
        creation_date=registro.original_creation_date,
        uuid_correlation=registro.uuid_correlation if manter_uuid else None
    )

@receiver(post_delete, sender=SettledEntry)
def atualizar_saldo_banco_apos_remocao(sender, instance, **kwargs):
    try:
        banco = Bancos.objects.get(id=instance.banco_id_liquidacao)  # Modificado para usar ID
        if instance.transaction_type == 'Crédito':
            banco.current_balance -= instance.amount  # Subtrai para créditos
        else:  # Débito
            banco.current_balance += instance.amount  # Adiciona para débitos
        banco.save()
    except Bancos.DoesNotExist:
        pass  # Tratar o caso em que o banco não é encontrado, se necessário

@csrf_exempt
def atualizar_lancamento(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lancamento = SettledEntry.objects.get(pk=id)
            
            # Assume que 'due_date' é a chave no JSON que contém a data no formato 'YYYY-MM-DD'
            due_date = data.get('due_date', None)
            if due_date:
                # Converte a data recebida para datetime, adicionando uma hora padrão se necessário
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                # Mantém a hora original da data_liquidacao ou define uma hora padrão (ex: meio-dia)
                hora_original = lancamento.data_liquidacao.time() if lancamento.data_liquidacao else datetime.time(12, 0)
                lancamento.data_liquidacao = datetime.combine(due_date, hora_original)
            
            lancamento.description = data.get('description', lancamento.description)
            lancamento.observation = data.get('observation', lancamento.observation)

            lancamento._skip_update_saldo = True
            
            lancamento.save()
            
            return JsonResponse({"message": "Lançamento atualizado com sucesso!"}, status=200)
        except SettledEntry.DoesNotExist:
            return JsonResponse({"error": "Lançamento não encontrado"}, status=404)
        except ValueError as e:
            # Captura erros na conversão da data
            return JsonResponse({"error": f"Erro ao processar a data: {str(e)}"}, status=400)

    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def atualizar_lancamentos_por_uuid(request, uuid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            due_date = data.get('novaData', None)
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                lancamentos = SettledEntry.objects.filter(uuid_correlation=uuid)
                for lancamento in lancamentos:
                    hora_original = lancamento.data_liquidacao.time() if lancamento.data_liquidacao else datetime.time(12, 0)
                    lancamento.data_liquidacao = datetime.combine(due_date, hora_original)
                    lancamento._skip_update_saldo = True
                    lancamento.save()
            
            return JsonResponse({"message": f"Lançamentos atualizados com sucesso para o UUID {uuid}!"}, status=200)
        except ValueError as e:
            return JsonResponse({"error": f"Erro ao processar a data: {str(e)}"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)