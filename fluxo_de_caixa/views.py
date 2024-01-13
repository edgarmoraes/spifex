from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from dateutil.relativedelta import relativedelta
from .models import Tabela_fluxo, TabelaTemporaria

def fluxo_de_caixa(request):
    if request.method == "GET":
        return exibir_fluxo_de_caixa(request)
    elif request.method == "POST":
        return processar_fluxo_de_caixa(request)
    
def calcular_saldo_acumulado(tabela_fluxo_list):
    """
    Calcula o saldo acumulado para cada entrada em uma lista de fluxos de caixa.
    :param tabela_fluxo_list: QuerySet de objetos Tabela_fluxo.
    :return: None. Modifica cada objeto Tabela_fluxo adicionando um atributo 'saldo'.
    """
    saldo_total = 0
    for fluxo_de_caixa in tabela_fluxo_list:
        if fluxo_de_caixa.natureza == 'Débito':
            saldo_total -= fluxo_de_caixa.valor
        else:
            saldo_total += fluxo_de_caixa.valor
        fluxo_de_caixa.saldo = saldo_total

def exibir_fluxo_de_caixa(request):
    """ Exibe a lista de fluxos de caixa """
    Tabela_fluxo_list = Tabela_fluxo.objects.all()
    calcular_saldo_acumulado(Tabela_fluxo_list)
    context = {'Tabela_fluxo_list': Tabela_fluxo_list}
    return render(request, 'fluxo_de_caixa.html', context)

def processar_fluxo_de_caixa(request):
    """ Processa o formulário de fluxo de caixa """
    dados = extrair_dados_formulario(request)
    if dados['lancamento_id']:
        atualizar_fluxo_existente(dados)
    else:
        criar_novos_fluxos(dados)
    return redirect(request.path)

def extrair_dados_formulario(request):
    """ Extrai e retorna os dados do formulário """
    return {
        'vencimento': datetime.strptime(request.POST.get('vencimento'), '%Y-%m-%d'),
        'descricao': request.POST.get('descricao'),
        'observacao': request.POST.get('observacao'),
        'valor': request.POST.get('valor'),
        'conta_contabil': request.POST.get('conta_contabil'),
        'parcelas': request.POST.get('parcelas', '1'),
        'tags': request.POST.get('tags'),
        'lancamento_id': request.POST.get('lancamento_id'),
        'natureza': 'Crédito' if 'salvar_recebimento' in request.POST else 'Débito',
        'total_parcelas': int(request.POST.get('parcelas', '1')) if request.POST.get('parcelas', '1').isdigit() else 1
    }

def atualizar_fluxo_existente(dados):
    """ Atualiza um fluxo de caixa existente """
    fluxo_de_caixa = get_object_or_404(Tabela_fluxo, id=dados['lancamento_id'])
    for campo, valor in dados.items():
        setattr(fluxo_de_caixa, campo, valor)
    fluxo_de_caixa.save()

def criar_novos_fluxos(dados):
    """ Cria novos registros de fluxo de caixa """
    for i in range(dados['total_parcelas']):
        vencimento_parcela = dados['vencimento'] + relativedelta(months=i)
        formato_parcela = f"{i + 1}/{dados['total_parcelas']}" if dados['total_parcelas'] > 1 else str(i + 1)
        Tabela_fluxo.objects.create(
            vencimento=vencimento_parcela,
            descricao=dados['descricao'],
            observacao=dados['observacao'],
            valor=dados['valor'],
            conta_contabil=dados['conta_contabil'],
            parcelas=formato_parcela,
            tags=dados['tags'],
            natureza=dados['natureza'],
            data_criacao=datetime.now()
        )

@csrf_exempt
def deletar_entradas(request):
    # Somente aceita solicitações POST
    if request.method == 'POST':
        ids_para_apagar = extrair_ids_para_apagar(request)
        processar_ids(ids_para_apagar)

        Tabela_fluxo_list = Tabela_fluxo.objects.all()
        calcular_saldo_acumulado(Tabela_fluxo_list)

        return JsonResponse({'status': 'success'})

def extrair_ids_para_apagar(request):
    """ Extrai os IDs do corpo da solicitação """
    data = json.loads(request.body)
    return data.get('ids', [])  # Retorna uma lista vazia se 'ids' não estiver presente

def processar_ids(ids_para_apagar):
    """ Processa cada ID para apagar o objeto correspondente e criar um registro na TabelaTemporaria """
    for id_str in ids_para_apagar:
        try:
            id = int(id_str)  # Convertendo o ID para inteiro
            objeto = Tabela_fluxo.objects.get(id=id)
            criar_registro_temporario(objeto)
            objeto.delete()  # Apagando o objeto original
        except Tabela_fluxo.DoesNotExist:
            # Se o ID não for encontrado, pula para o próximo
            continue

def criar_registro_temporario(objeto):
    """ Cria um novo registro na TabelaTemporaria com base no objeto da Tabela_fluxo """
    TabelaTemporaria.objects.create(
        vencimento=objeto.vencimento,
        descricao=objeto.descricao,
        observacao=objeto.observacao,
        valor=objeto.valor,
        conta_contabil=objeto.conta_contabil,
        parcelas=objeto.parcelas,
        tags=objeto.tags,
        natureza=objeto.natureza,
        data_criacao=objeto.data_criacao
    )
