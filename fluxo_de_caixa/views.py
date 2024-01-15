from django.shortcuts import render, redirect, get_object_or_404
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models.signals import post_save, post_delete
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from .models import Tabela_fluxo, TabelaTemporaria, TotaisMes

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
    """ Exibe a lista de fluxos de caixa junto com os totais de cada mês """
    Tabela_fluxo_list = Tabela_fluxo.objects.all().order_by('vencimento')
    calcular_saldo_acumulado(Tabela_fluxo_list)

    # Obter os totais de cada mês
    totais_mes = TotaisMes.objects.all()

    # Adicionar os totais ao contexto
    context = {
        'Tabela_fluxo_list': Tabela_fluxo_list,
        'totais_mes': totais_mes
    }
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

# Sinal para atualizar TotaisMes quando um FluxoDeCaixa for salvo
def atualizar_totais_mes(data_formatada):
    """ Cria um registro único de cada mês, calculando o total de crédito e débito e saldo """
    inicio_mes = datetime.strptime(data_formatada, '%b/%Y').replace(day=1)
    fim_mes = inicio_mes + relativedelta(months=1, days=-1)

    total_credito = Tabela_fluxo.objects.filter(
        vencimento__range=(inicio_mes, fim_mes), 
        natureza='Crédito'
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    total_debito = Tabela_fluxo.objects.filter(
        vencimento__range=(inicio_mes, fim_mes), 
        natureza='Débito'
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    obj, created = TotaisMes.objects.get_or_create(data_formatada=data_formatada)
    obj.total_credito = total_credito
    obj.total_debito = total_debito
    obj.saldo_mensal = total_credito - total_debito
    obj.save()

@receiver(post_save, sender=Tabela_fluxo)
def save_update_data_unica(sender, instance, **kwargs):
    data_formatada = instance.vencimento.strftime('%b/%Y')
    atualizar_totais_mes(data_formatada)

@receiver(post_delete, sender=Tabela_fluxo)
def delete_update_data_unica(sender, instance, **kwargs):
    data_formatada = instance.vencimento.strftime('%b/%Y')

    # Verificar se ainda existem lançamentos para esse mês
    if not Tabela_fluxo.objects.filter(vencimento__year=instance.vencimento.year, vencimento__month=instance.vencimento.month).exists():
        # Se não existirem, excluir o registro de TotaisMes
        TotaisMes.objects.filter(data_formatada=data_formatada).delete()
    else:
        # Caso contrário, atualizar os totais
        atualizar_totais_mes(data_formatada)

def meses_filtro(request):
    totais_mes = TotaisMes.objects.all()
    context = {'totais_mes': totais_mes}
    return render(request, 'fluxo_de_caixa.html', context)

def filtrar_lancamentos(request):
    contas_contabeis = request.GET.get('contas_contabeis')
    meses = request.GET.get('meses')
    bancos = request.GET.get('bancos')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    natureza = request.GET.get('natureza')
    caixa_pesquisa = request.GET.get('caixa_pesquisa')
    caixa_pesquisa_tags = request.GET.get('caixa_pesquisa_tags')

    Tabela_fluxo_list = Tabela_fluxo.objects.all().order_by('vencimento')

    if contas_contabeis:
        Tabela_fluxo_list = Tabela_fluxo_list.filter(conta_contabil=contas_contabeis)

    if bancos:
        Tabela_fluxo_list = Tabela_fluxo_list.filter(bancos=bancos)

    if contas_contabeis:
        Tabela_fluxo_list = Tabela_fluxo_list.filter(conta_contabil=contas_contabeis)

    if data_inicio:
        Tabela_fluxo_list = Tabela_fluxo_list.filter(vencimento__gte=datetime.strptime(data_inicio, '%Y-%m-%d'))

    if data_fim:
        Tabela_fluxo_list = Tabela_fluxo_list.filter(vencimento__lte=datetime.strptime(data_fim, '%Y-%m-%d'))

    return render(request, 'fluxo_de_caixa.html', {'Tabela_fluxo_list': Tabela_fluxo_list})