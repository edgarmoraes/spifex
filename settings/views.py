import uuid
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from cash_flow.models import Banks, Departments, Inventory, Entities
from settled_entry.models import SettledEntry
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
    
def inventory(request):
    if request.method =="GET":
        inventory_list = Inventory.objects.all().order_by('id')

        context = {
            'Inventory_list': inventory_list,
        }
        return render(request, 'inventory.html', context)
    
def entities(request):
    if request.method =="GET":
        entities_list = Entities.objects.all().order_by('id')

        context = {
            'Entities_list': entities_list,
        }
        return render(request, 'entities.html', context)
    
@csrf_exempt
def save_bank(request):
    # Retorna erro se não for uma requisição POST
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método não permitido."}, status=405)
    
    initial_balance_str = request.POST.get('bank_initial_balance', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    initial_balance = Decimal(initial_balance_str) if initial_balance_str else Decimal('0.00')

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
        banks_table.initial_balance = initial_balance
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
    department_id = request.POST.get('department_id')
    department_name = request.POST.get('department')

    if department_id:
        # Atualizar um department existente
        try:
            department_list = Departments.objects.get(pk=department_id)
            # Verifica se o nome é diferente para evitar conflito de nome único
            if department_list.department != department_name and Departments.objects.filter(department=department_name).exists():
                return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome diferente para o departmento.'})
            department_list.department = department_name
            department_list.save()
            return JsonResponse({'success': True, 'message': 'Departamento atualizado com sucesso.'})
        except Departments.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Departamento não encontrado.'})
    else:
        # Criar um novo department
        if Departments.objects.filter(department=department_name).exists():
            return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome diferente para o departmento.'})
        
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
    
@require_POST
def save_inventory(request):
    inventory_item_id = request.POST.get('inventory_item_id')
    inventory_item = request.POST.get('inventory_item')
    inventory_item_code = request.POST.get('inventory_item_code')
    inventory_quantity = request.POST.get('inventory_quantity')

    if inventory_item_id:
        # Atualizar um item existente
        try:
            inventory_list = Inventory.objects.get(pk=inventory_item_id)
            # Verifica se o nome ou o código são diferentes para evitar conflito de nome ou código únicos
            if (inventory_list.inventory_item != inventory_item and Inventory.objects.filter(inventory_item=inventory_item).exists()) or \
               (inventory_list.inventory_item_code != inventory_item_code and Inventory.objects.filter(inventory_item_code=inventory_item_code).exists()):
                return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome ou código diferente para o item.'})
            inventory_list.inventory_item_code = inventory_item_code
            inventory_list.inventory_item = inventory_item
            inventory_list.inventory_quantity = inventory_quantity
            inventory_list.save()
            return JsonResponse({'success': True, 'message': 'Item atualizado com sucesso.'})
        except Inventory.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item não encontrado.'})
    else:
        # Criar um novo item
        if Inventory.objects.filter(inventory_item=inventory_item).exists() or Inventory.objects.filter(inventory_item_code=inventory_item_code).exists():
            return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome ou código diferente para o item.'})
        
        new_item = Inventory(
            inventory_item_code=inventory_item_code,
            inventory_item=inventory_item,
            inventory_quantity=inventory_quantity,
            uuid_inventory_item=uuid.uuid4()
        )
        new_item.save()

        return JsonResponse({'success': True, 'message': 'Item adicionado com sucesso.'})

@require_POST
def verify_and_delete_inventory(request, inventory_item_id):
    try:
        # Tenta encontrar e excluir o inventory
        inventory_list = Inventory.objects.get(pk=inventory_item_id)
        inventory_list.delete()
        # Item excluído com sucesso
        return JsonResponse({'success': True})
    except Inventory.DoesNotExist:
        # Item não encontrado
        return JsonResponse({'success': False, 'error': 'Item não encontrado.'})
    
@require_POST
def save_entity(request):
    entity_id = request.POST.get('entity_id')
    entity_type = request.POST.get('entity_type') or None
    full_name = request.POST.get('full_name') or None
    tax_id = request.POST.get('tax_id') or None
    alias_name = request.POST.get('alias_name') or None
    area_code = request.POST.get('area_code') or None
    phone_number = request.POST.get('phone_number') or None
    street = request.POST.get('street') or None
    street_number = request.POST.get('street_number') or None
    state = request.POST.get('state') or None
    city = request.POST.get('city') or None
    postal_code = request.POST.get('postal_code') or None
    email = request.POST.get('email') or None
    bank_name = request.POST.get('bank_name') or None
    bank_branch = request.POST.get('bank_branch') or None
    checking_account = request.POST.get('checking_account') or None
    account_holder_tax_id = request.POST.get('account_holder_tax_id') or None
    account_holder_name = request.POST.get('account_holder_name') or None

    # Determine the appropriate tax ID field
    if tax_id and len(tax_id) <= 14:
        ssn_tax_id = tax_id
        ein_tax_id = None
    else:
        ssn_tax_id = None
        ein_tax_id = tax_id

    # Determine success messages based on entity type
    if entity_type == 'customer':
        update_message = 'Cliente atualizado com sucesso.'
        add_message = 'Cliente adicionado com sucesso.'
    elif entity_type == 'supplier':
        update_message = 'Fornecedor atualizado com sucesso.'
        add_message = 'Fornecedor adicionado com sucesso.'
    elif entity_type == 'employee':
        update_message = 'Funcionário atualizado com sucesso.'
        add_message = 'Funcionário adicionado com sucesso.'
    else:
        update_message = 'Entidade atualizada com sucesso.'
        add_message = 'Entidade adicionada com sucesso.'

    if entity_id:
        # Update existing entity
        try:
            entity = Entities.objects.get(pk=entity_id)
            if (ssn_tax_id and ssn_tax_id != entity.ssn_tax_id and Entities.objects.filter(ssn_tax_id=ssn_tax_id).exists()) or \
               (ein_tax_id and ein_tax_id != entity.ein_tax_id and Entities.objects.filter(ein_tax_id=ein_tax_id).exists()):
                return JsonResponse({'success': False, 'message': 'Por favor, escolha um CPF/CNPJ diferente para a entidade.'})
            entity.entity_type = entity_type
            entity.full_name = full_name
            entity.ssn_tax_id = ssn_tax_id
            entity.ein_tax_id = ein_tax_id
            entity.alias_name = alias_name
            entity.area_code = area_code
            entity.phone_number = phone_number
            entity.street = street
            entity.street_number = street_number
            entity.state = state
            entity.city = city
            entity.postal_code = postal_code
            entity.email = email
            entity.bank_name = bank_name
            entity.bank_branch = bank_branch
            entity.checking_account = checking_account
            entity.account_holder_tax_id = account_holder_tax_id
            entity.account_holder_name = account_holder_name
            entity.save()
            return JsonResponse({'success': True, 'message': update_message})
        except Entities.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Entidade não encontrada.'})
    else:
        # Create new entity
        if (ssn_tax_id and Entities.objects.filter(ssn_tax_id=ssn_tax_id).exists()) or \
           (ein_tax_id and Entities.objects.filter(ein_tax_id=ein_tax_id).exists()):
            return JsonResponse({'success': False, 'message': 'Por favor, escolha um CPF/CNPJ diferente para a entidade.'})
        
        new_entity = Entities(
            entity_type=entity_type,
            full_name=full_name,
            ssn_tax_id=ssn_tax_id,
            ein_tax_id=ein_tax_id,
            alias_name=alias_name,
            area_code=area_code,
            phone_number=phone_number,
            street=street,
            street_number=street_number,
            state=state,
            city=city,
            postal_code=postal_code,
            email=email,
            bank_name=bank_name,
            bank_branch=bank_branch,
            checking_account=checking_account,
            account_holder_tax_id=account_holder_tax_id,
            account_holder_name=account_holder_name,
            uuid_entities=uuid.uuid4()
        )
        new_entity.save()

        return JsonResponse({'success': True, 'message': add_message})
    
@require_POST
def verify_and_delete_entity(request, entity_id):
    try:
        # Tenta encontrar e excluir a entidade
        entity = Entities.objects.get(pk=entity_id)
        entity.delete()
        # Entidade excluída com sucesso
        return JsonResponse({'success': True, 'message': 'Entidade excluída com sucesso.'})
    except Entities.DoesNotExist:
        # Entidade não encontrada
        return JsonResponse({'success': False, 'error': 'Entidade não encontrada.'})
    except Exception as e:
        # Outro erro
        return JsonResponse({'success': False, 'error': str(e)})