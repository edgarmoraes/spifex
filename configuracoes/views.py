from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from fluxo_de_caixa.models import Bancos
from django.views.decorators.csrf import csrf_exempt

def configuracoes(request):
    if request.method =="GET":
        return render(request, 'configuracoes.html')

def bancos_e_contas(request):
    if request.method =="GET":
        lista_bancos = Bancos.objects.all().order_by('id')

        context = {
            'bancos': lista_bancos,
        }
        return render(request, 'bancos_e_contas.html', context)
    
@csrf_exempt
def salvar_banco(request):
    if request.method == 'POST':
        id_banco = request.POST.get('id_banco')
        descricao = request.POST.get('descricao')
        agencia = request.POST.get('agencia')
        conta = request.POST.get('conta')
        saldo_inicial = Decimal(request.POST.get('saldo-inicial').replace(',', '.'))
        status_banco = request.POST.get('status-banco') == 'ativo'

        if id_banco:  # Atualização
            banco = Bancos.objects.get(pk=id_banco)
            banco.banco = descricao
            banco.agencia = agencia
            banco.conta = conta
            banco.saldo_inicial = saldo_inicial
            banco.status = status_banco
        else:  # Criação
            banco = Bancos(
                banco=descricao,
                agencia=agencia,
                conta=conta,
                saldo_inicial=saldo_inicial,
                status=status_banco
            )

        banco.save()

        # Resposta JSON para atualização dinâmica
        return JsonResponse({"success": True, "id": banco.id})

    # Caso não seja POST, retorna erro
    return JsonResponse({"success": False}, status=400)