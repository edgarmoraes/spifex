import uuid
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from cash_flow.models import Banks, Departments
from realizado.models import SettledEntry
from django.db.models import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def settings(request):
    if request.method =="GET":
        return render(request, 'settings.html')

def banks(request):
    if request.method =="GET":
        banks_list = Banks.objects.all().order_by('id')

        context = {
            'Banks_list': banks_list,
        }
        return render(request, 'banks_and_accounts.html', context)
    
def departments(request):
    if request.method =="GET":
        departments_list = Departments.objects.all().order_by('id')

        context = {
            'Departments_list': departments_list,
        }
        return render(request, 'departments.html', context)
    
@csrf_exempt
def save_bank(request):
    # Retorna erro se não for uma requisição POST
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método não permitido."}, status=405)
    
    opening_balance_str = request.POST.get('saldo-inicial', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    opening_balance = Decimal(opening_balance_str) if opening_balance_str else Decimal('0.00')

    bank_id = request.POST.get('bank_id')
    bank_name = request.POST.get('bank_name')
    bank_branch = request.POST.get('bank_branch')
    bank_account = request.POST.get('bank_account')
    bank_status = request.POST.get('bank_status') == 'ativo'

    try:
        if bank_id:  # Atualização
            banks_table = Banks.objects.get(pk=bank_id)
            was_updated = banks_table.banco != bank_name  # Verifica se a descrição do banco foi atualizada
        else:  # Criação
            banks_table = Banks()
            was_updated = False

        banks_table.banco = bank_name
        banks_table.bank_branch = bank_branch
        banks_table.bank_account = bank_account
        banks_table.initial_balance = opening_balance
        banks_table.bank_status = bank_status
        banks_table.save()

        # Se a descrição do banco foi atualizada, atualiza também em SettledEntry
        if was_updated:
            SettledEntry.objects.filter(settlement_bank_id=banks_table.id).update(settlement_bank=bank_name)

        # Resposta JSON para atualização dinâmica
        return JsonResponse({"success": True, "id": banks_table.id})
    except ObjectDoesNotExist:
        # Banco não encontrado para atualização
        return JsonResponse({"success": False, "error": "Banco não encontrado."}, status=404)

@require_POST
def verify_and_delete_bank(request, bank_id):
    # Verifica se o banco está sendo utilizado na SettledEntry
    if SettledEntry.objects.filter(settlement_bank_id=bank_id).exists():
        # Banco está sendo utilizado, não pode ser excluído
        return JsonResponse({'success': False, 'error': 'Este banco está sendo utilizado e não pode ser excluído.'})

    try:
        # Tenta encontrar e excluir o banco
        bank_to_detele = Banks.objects.get(pk=bank_id)
        bank_to_detele.delete()
        # Banco excluído com sucesso
        return JsonResponse({'success': True})
    except Banks.DoesNotExist:
        # Banco não encontrado
        return JsonResponse({'success': False, 'error': 'Banco não encontrado.'})
    
@require_POST
def save_department(request):
    department_id = request.POST.get('id_department')
    department_name = request.POST.get('department')

    if department_id:
        # Atualizar um department existente
        try:
            department_list = Departments.objects.get(pk=department_id)
            # Verifica se o nome é diferente para evitar conflito de nome único
            if department_list.department != department_name and Departments.objects.filter(department=department_name).exists():
                return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome diferente para o department.'})
            department_list.department = department_name
            department_list.save()
            return JsonResponse({'success': True, 'message': 'Departamento atualizado com sucesso.'})
        except Departments.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Departamento não encontrado.'})
    else:
        # Criar um novo department
        if Departments.objects.filter(department=department_name).exists():
            return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome diferente para o department.'})
        
        new_department = Departments(
            department=department_name,
            uuid_department=uuid.uuid4()
        )
        new_department.save()

        return JsonResponse({'success': True, 'message': 'Departamento adicionado com sucesso.'})

@require_POST
def verify_and_delete_department(request, department_id):
    try:
        # Tenta encontrar e excluir o department
        department_list = Departments.objects.get(pk=department_id)
        department_list.delete()
        # Departamento excluído com sucesso
        return JsonResponse({'success': True})
    except Departments.DoesNotExist:
        # Departamento não encontrado
        return JsonResponse({'success': False, 'error': 'Departamento não encontrado.'})