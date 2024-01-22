from django.shortcuts import render
from django.db.models import Sum
from fluxo_de_caixa.models import Tabela_fluxo, TabelaTemporaria, TotaisMes, Bancos

def realizado(request):
    if request.method == "GET":
        return exibir_realizado(request)
    


def exibir_realizado(request):
    """ Exibe a lista de fluxos de caixa junto com os totais de cada mês e bancos """
    bancos_ativos = Bancos.objects.filter(status=True)
    saldo_total_bancos = bancos_ativos.aggregate(Sum('saldo_inicial'))['saldo_inicial__sum'] or 0
    Tabela_fluxo_list = Tabela_fluxo.objects.all().order_by('vencimento')
    calcular_saldo_acumulado(Tabela_fluxo_list, saldo_total_bancos)
    totais_mes = TotaisMes.objects.all()
    context = {
        'Tabela_fluxo_list': Tabela_fluxo_list,
        'totais_mes': totais_mes,
        'bancos': bancos_ativos,
        'saldo_total_bancos': saldo_total_bancos
    }
    return render(request, 'realizado.html', context)

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

def exibir_bancos(request):
    bancos = Bancos.objects.all()
    return render(request, 'realizado.html', {'bancos': bancos})