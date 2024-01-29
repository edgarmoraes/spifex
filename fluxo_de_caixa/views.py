from django.shortcuts import render, redirect, get_object_or_404
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models.signals import post_save, post_delete
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from .models import Tabela_fluxo, TabelaTemporaria, Totais_mes_fluxo, Bancos

def fluxo_de_caixa(request):
    if request.method == "GET":
        return exibir_fluxo_de_caixa(request)
    elif request.method == "POST":
        return processar_fluxo_de_caixa(request)

def exibir_fluxo_de_caixa(request):
    """ Exibe a lista de fluxos de caixa junto com os totais de cada mês e bancos """
    bancos_ativos = Bancos.objects.filter(status=True)
    saldo_total_bancos = bancos_ativos.aggregate(Sum('saldo_inicial'))['saldo_inicial__sum'] or 0
    Tabela_fluxo_list = Tabela_fluxo.objects.all().order_by('vencimento')
    calcular_saldo_acumulado(Tabela_fluxo_list, saldo_total_bancos)
    totais_mes_fluxo = Totais_mes_fluxo.objects.all()
    context = {
        'Tabela_fluxo_list': Tabela_fluxo_list,
        'totais_mes_fluxo': totais_mes_fluxo,
        'bancos': bancos_ativos,
        'saldo_total_bancos': saldo_total_bancos
    }
    return render(request, 'fluxo_de_caixa.html', context)

def calcular_saldo_acumulado(tabela_fluxo_list, saldo_inicial):
    """ Calcula o saldo acumulado para cada entrada em uma lista de fluxos de caixa.
    :param tabela_fluxo_list: QuerySet de objetos Tabela_fluxo.
    :return: None. Modifica cada objeto Tabela_fluxo adicionando um atributo 'saldo' """
    saldo_total = saldo_inicial
    for fluxo_de_caixa in tabela_fluxo_list:
        if fluxo_de_caixa.natureza == 'Débito':
            saldo_total -= fluxo_de_caixa.valor
        else:
            saldo_total += fluxo_de_caixa.valor
        fluxo_de_caixa.saldo = saldo_total

def processar_fluxo_de_caixa(request):
    dados = extrair_dados_formulario(request)

    if dados['lancamento_id']:
        if dados['parcelas_total'] > 1:
            if dados['parcelas_total_originais'] > 1:
                atualizar_fluxo_existente(dados)  # Manter parcelas_total se for uma série de parcelas
            else:
                # Criar novos fluxos se o número de parcelas foi alterado para mais de um
                Tabela_fluxo.objects.filter(id=dados['lancamento_id']).delete()
                criar_novos_fluxos(dados)
        else:
            atualizar_fluxo_existente(dados)  # Atualização normal para lançamentos de uma única parcela
    else:
        criar_novos_fluxos(dados)
    return redirect(request.path)

def extrair_dados_formulario(request):
    """ Extrai e retorna os dados do formulário """
    lancamento_id = request.POST.get('lancamento_id')
    lancamento_id = None if lancamento_id == '' else lancamento_id
    return {
        'vencimento': datetime.strptime(request.POST.get('vencimento'), '%Y-%m-%d'),
        'descricao': request.POST.get('descricao'),
        'observacao': request.POST.get('observacao'),
        'valor': request.POST.get('valor'),
        'conta_contabil': request.POST.get('conta_contabil'),
        'parcelas_total': int(request.POST.get('parcelas', '1')) if request.POST.get('parcelas', '1').isdigit() else 1,
        'parcelas_total_originais': int(request.POST.get('parcelas_total_originais', '1')),
        'tags': request.POST.get('tags'),
        'lancamento_id': lancamento_id,
        'natureza': 'Crédito' if 'salvar_recebimento' in request.POST else 'Débito',
    }

def atualizar_fluxo_existente(dados):
    fluxo_de_caixa = get_object_or_404(Tabela_fluxo, id=dados['lancamento_id'])
    parcelas_total_originais = fluxo_de_caixa.parcelas_total  # Obter o valor original de parcelas_total

    for campo, valor in dados.items():
        # Não atualizar parcelas_total se for um lançamento de múltiplas parcelas
        if campo == 'parcelas_total' and parcelas_total_originais > 1:
            continue
        setattr(fluxo_de_caixa, campo, valor)
    fluxo_de_caixa.save()

def criar_novos_fluxos(dados, iniciar_desde_o_atual=False):
    parcela_inicial = dados.get('parcela_atual', 1)
    total_parcelas = dados['parcelas_total']

    for i in range(parcela_inicial, total_parcelas + 1):
        vencimento_parcela = dados['vencimento'] + relativedelta(months=i - parcela_inicial)
        Tabela_fluxo.objects.create(
            vencimento=vencimento_parcela,
            descricao=dados['descricao'],
            observacao=dados['observacao'],
            valor=dados['valor'],
            conta_contabil=dados['conta_contabil'],
            parcela_atual=i,
            parcelas_total=total_parcelas,
            tags=dados['tags'],
            natureza=dados['natureza'],
            data_criacao=datetime.now()
        )

@csrf_exempt
def deletar_entradas(request):
    if request.method == 'POST':
        ids_para_apagar = extrair_ids_para_apagar(request)
        processar_ids(ids_para_apagar)

        Tabela_fluxo_list = Tabela_fluxo.objects.all()
        saldo_total_bancos = Bancos.objects.filter(status=True).aggregate(Sum('saldo_inicial'))['saldo_inicial__sum'] or 0
        calcular_saldo_acumulado(Tabela_fluxo_list, saldo_total_bancos)

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
        parcela_atual=objeto.parcela_atual,
        parcelas_total=objeto.parcelas_total,
        tags=objeto.tags,
        natureza=objeto.natureza,
        data_criacao=objeto.data_criacao
    )


# SIGNAL HANDLERS ############################################################################

@receiver(post_save, sender=Tabela_fluxo)
def save_update_data_unica(sender, instance, **kwargs):
    data_formatada = instance.vencimento.strftime('%b/%Y')
    atualizar_totais_mes(data_formatada)

@receiver(post_delete, sender=Tabela_fluxo)
def delete_update_data_unica(sender, instance, **kwargs):
    data_formatada = instance.vencimento.strftime('%b/%Y')
    if not Tabela_fluxo.objects.filter(vencimento__year=instance.vencimento.year, vencimento__month=instance.vencimento.month).exists():
        Totais_mes_fluxo.objects.filter(data_formatada=data_formatada).delete()
    else:
        atualizar_totais_mes(data_formatada)

def atualizar_totais_mes(data_formatada):
    """ Sinal para atualizar Totais_mes_fluxo quando um FluxoDeCaixa for salvo """
    # Calculando as datas de início e fim do mês
    inicio_mes = datetime.strptime(data_formatada, '%b/%Y').replace(day=1)
    fim_mes = inicio_mes + relativedelta(months=1, days=-1)

    # Calculando totais de crédito e débito
    total_credito = Tabela_fluxo.objects.filter(
        vencimento__range=(inicio_mes, fim_mes),
        natureza='Crédito'
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    total_debito = Tabela_fluxo.objects.filter(
        vencimento__range=(inicio_mes, fim_mes),
        natureza='Débito'
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    # Atualizar ou criar registro em Totais_mes_fluxo
    Totais_mes_fluxo.objects.update_or_create(
        data_formatada=data_formatada,
        defaults={
            'inicio_mes': inicio_mes,
            'fim_mes': fim_mes,
            'total_credito': total_credito,
            'total_debito': total_debito,
            'saldo_mensal': total_credito - total_debito
        }
    )

# FUNÇÕES ÚNICAS ############################################################################

def meses_filtro(request):
    totais_mes_fluxo = Totais_mes_fluxo.objects.all().order_by('data_formatada')
    context = {'totais_mes_fluxo': totais_mes_fluxo}
    return render(request, 'fluxo_de_caixa.html', context)

def exibir_bancos(request):
    bancos = Bancos.objects.all()
    return render(request, 'fluxo_de_caixa.html', {'bancos': bancos})
