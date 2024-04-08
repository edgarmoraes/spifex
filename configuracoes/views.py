import json
import uuid
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from fluxo_de_caixa.models import Banks, Departamentos
from realizado.models import SettledEntry
from django.db.models import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def configuracoes(request):
    if request.method =="GET":
        return render(request, 'configuracoes.html')

def bancos_e_contas(request):
    if request.method =="GET":
        lista_bancos = Banks.objects.all().order_by('id')

        context = {
            'Banks_list': lista_bancos,
        }
        return render(request, 'bancos_e_contas.html', context)
    
def departments(request):
    if request.method =="GET":
        lista_departamentos = Departamentos.objects.all().order_by('id')

        context = {
            'departamentos': lista_departamentos,
        }
        return render(request, 'departments.html', context)
    
@csrf_exempt
def salvar_banco(request):
    # Retorna erro se não for uma requisição POST
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método não permitido."}, status=405)
    
    saldo_inicial_str = request.POST.get('saldo-inicial', 'R$ 0,00').replace('R$ ', '').replace('.', '').replace(',', '.')
    saldo_inicial = Decimal(saldo_inicial_str) if saldo_inicial_str else Decimal('0.00')

    id_banco = request.POST.get('id_banco')
    descricao = request.POST.get('descricao')
    agencia = request.POST.get('agencia')
    conta = request.POST.get('conta')
    status_banco = request.POST.get('status-banco') == 'ativo'

    try:
        if id_banco:  # Atualização
            banco = Banks.objects.get(pk=id_banco)
            was_updated = banco.banco != descricao  # Verifica se a descrição do banco foi atualizada
        else:  # Criação
            banco = Banks()
            was_updated = False

        banco.banco = descricao
        banco.agencia = agencia
        banco.conta = conta
        banco.saldo_inicial = saldo_inicial
        banco.status = status_banco
        banco.save()

        # Se a descrição do banco foi atualizada, atualiza também em SettledEntry
        if was_updated:
            SettledEntry.objects.filter(banco_id_liquidacao=banco.id).update(banco_liquidacao=descricao)

        # Resposta JSON para atualização dinâmica
        return JsonResponse({"success": True, "id": banco.id})
    except ObjectDoesNotExist:
        # Banco não encontrado para atualização
        return JsonResponse({"success": False, "error": "Banco não encontrado."}, status=404)

@require_POST
def verificar_e_excluir_banco(request, idBanco):
    # Verifica se o banco está sendo utilizado na SettledEntry
    if SettledEntry.objects.filter(banco_id_liquidacao=idBanco).exists():
        # Banco está sendo utilizado, não pode ser excluído
        return JsonResponse({'success': False, 'error': 'Este banco está sendo utilizado e não pode ser excluído.'})

    try:
        # Tenta encontrar e excluir o banco
        banco = Banks.objects.get(pk=idBanco)
        banco.delete()
        # Banco excluído com sucesso
        return JsonResponse({'success': True})
    except Banks.DoesNotExist:
        # Banco não encontrado
        return JsonResponse({'success': False, 'error': 'Banco não encontrado.'})
    
@require_POST
def salvar_departamento(request):
    id_departamento = request.POST.get('id_departamentos')
    nome_departamento = request.POST.get('departamento')

    if id_departamento:
        # Atualizar um departamento existente
        try:
            departamento = Departamentos.objects.get(pk=id_departamento)
            # Verifica se o nome é diferente para evitar conflito de nome único
            if departamento.departamento != nome_departamento and Departamentos.objects.filter(departamento=nome_departamento).exists():
                return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome diferente para o departamento.'})
            departamento.departamento = nome_departamento
            departamento.save()
            return JsonResponse({'success': True, 'message': 'Departamento atualizado com sucesso.'})
        except Departamentos.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Departamento não encontrado.'})
    else:
        # Criar um novo departamento
        if Departamentos.objects.filter(departamento=nome_departamento).exists():
            return JsonResponse({'success': False, 'message': 'Por favor, escolha um nome diferente para o departamento.'})
        
        novo_departamento = Departamentos(
            departamento=nome_departamento,
            uuid_departamento=uuid.uuid4()
        )
        novo_departamento.save()

        return JsonResponse({'success': True, 'message': 'Departamento adicionado com sucesso.'})

@require_POST
def verificar_e_excluir_departamento(request, idDepartamento):
    try:
        # Tenta encontrar e excluir o departamento
        departamento = Departamentos.objects.get(pk=idDepartamento)
        departamento.delete()
        # Departamento excluído com sucesso
        return JsonResponse({'success': True})
    except Departamentos.DoesNotExist:
        # Departamento não encontrado
        return JsonResponse({'success': False, 'error': 'Departamento não encontrado.'})