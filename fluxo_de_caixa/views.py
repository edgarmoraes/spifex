import json
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.dispatch import receiver
from django.http import JsonResponse
from realizado.models import Tabela_realizado
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tabela_fluxo, TabelaTemporaria, Totais_mes_fluxo, Bancos

def fluxo_de_caixa(request):
    if request.method == "GET":
        return exibir_fluxo_de_caixa(request)
    elif request.method == "POST":
        return processar_fluxo_de_caixa(request)

def exibir_fluxo_de_caixa(request):
    """ Exibe a lista de fluxos de caixa junto com os totais de cada mês """
    bancos_ativos = Bancos.objects.filter(status=True)
    Tabela_fluxo_list = Tabela_fluxo.objects.all().order_by('vencimento', '-valor', 'descricao')
    totais_mes_fluxo = Totais_mes_fluxo.objects.all()
    context = {
        'Tabela_fluxo_list': Tabela_fluxo_list,
        'totais_mes_fluxo': totais_mes_fluxo,
        'bancos': bancos_ativos,
    }
    return render(request, 'fluxo_de_caixa.html', context)

def processar_fluxo_de_caixa(request):
    if 'transferencias' in request.POST and request.POST['transferencias'] == 'transferencia':
        return processar_transferencia(request)
    else:
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
    """Extrai e retorna os dados do formulário."""
    natureza = 'Crédito' if 'salvar_recebimento' in request.POST else 'Débito'
    
    # Escolhe o campo de ID correto com base na natureza da transação
    lancamento_id_recebimentos = request.POST.get('lancamento_id_recebimentos')
    lancamento_id_pagamentos = request.POST.get('lancamento_id_pagamentos')
    
    lancamento_id = None  # Inicialmente definido como None
    
    if natureza == 'Crédito' and lancamento_id_recebimentos:
        lancamento_id = int(lancamento_id_recebimentos)
    elif natureza == 'Débito' and lancamento_id_pagamentos:
        lancamento_id = int(lancamento_id_pagamentos)
    
    # Verifica e processa o campo 'vencimento'
    vencimento_str = request.POST.get('vencimento')
    vencimento = datetime.strptime(vencimento_str, '%Y-%m-%d') if vencimento_str else None

    # Processa outros campos com segurança
    descricao = request.POST.get('descricao', '')
    observacao = request.POST.get('observacao', '')
    valor = request.POST.get('valor', '0.00')
    conta_contabil = request.POST.get('conta_contabil', '')
    parcelas = request.POST.get('parcelas', '1')
    parcelas_total = int(parcelas) if parcelas.isdigit() else 1
    parcelas_total_originais = int(request.POST.get('parcelas_total_originais', '1'))
    tags = request.POST.get('tags', '')

    # Retorna um dicionário com os dados processados
    return {
        'vencimento': vencimento,
        'descricao': descricao,
        'observacao': observacao,
        'valor': valor,
        'conta_contabil': conta_contabil,
        'parcelas_total': parcelas_total,
        'parcelas_total_originais': parcelas_total_originais,
        'tags': tags,
        'lancamento_id': lancamento_id,
        'natureza': natureza,
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
    if 'vencimento' not in dados or dados['vencimento'] is None:
        # Trata o caso onde 'vencimento' não é fornecido ou é None
        # Você pode definir uma data padrão ou retornar um erro
        return JsonResponse({'error': 'Data de vencimento é necessária.'}, status=400)

    parcela_inicial = dados.get('parcela_atual', 1)
    total_parcelas = dados['parcelas_total']

    # Verifica se 'vencimento' já é um objeto datetime.datetime
    if isinstance(dados['vencimento'], datetime):
        vencimento_base = dados['vencimento'].date()
    else:
        # Converte de string para datetime.datetime se 'vencimento' for uma string
        vencimento_base = datetime.strptime(dados['vencimento'], '%Y-%m-%d').date()

    for i in range(parcela_inicial, total_parcelas + 1):
        vencimento_parcela = vencimento_base + relativedelta(months=i - parcela_inicial)
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

def processar_transferencia(request):
    data_transferencia = request.POST.get('data')
    valor_transferencia = Decimal(request.POST.get('valor').replace(',', '.'))
    banco_saida = request.POST.get('banco_saida')
    banco_entrada = request.POST.get('banco_entrada')
    observacao = request.POST.get('observacao')
    
    data_liquidacao = datetime.strptime(data_transferencia, '%Y-%m-%d')

    if banco_saida == banco_entrada:
        messages.error(request, "O banco de saída não pode ser igual ao banco de entrada. Por favor, selecione bancos diferentes.")
        return redirect('fluxo_de_caixa')  # Substitua 'fluxo_de_caixa' pelo nome correto da sua URL, se necessário
    # Cria o lançamento de saída
    lancamento_saida = Tabela_realizado(
        vencimento=data_liquidacao,
        descricao='Transferência para '+banco_entrada,
        observacao=observacao,
        valor=valor_transferencia,
        conta_contabil='Transferência Saída',
        parcela_atual=1,
        parcelas_total=1,
        tags='Transferência',
        natureza='Débito',
        original_data_criacao=datetime.now(),
        data_liquidacao=data_liquidacao,
        banco_liquidacao=banco_saida
    )
    lancamento_saida.save()

    # Cria o lançamento de entrada
    lancamento_entrada = Tabela_realizado(
        vencimento=data_liquidacao,
        descricao='Transferência de '+banco_saida,
        observacao=observacao,
        valor=valor_transferencia,
        conta_contabil='Transferência Entrada',
        parcela_atual=1,
        parcelas_total=1,
        tags='Transferência',
        natureza='Crédito',
        original_data_criacao=datetime.now(),
        data_liquidacao=data_liquidacao,
        banco_liquidacao=banco_entrada
    )
    lancamento_entrada.save()

    return redirect(request.path)

@csrf_exempt
def processar_liquidacao(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        ids_para_excluir = []

        for item in dados:
            try:
                registro_original = Tabela_fluxo.objects.get(id=item['id'])
                valor_decimal = Decimal(item['valor'])
                
                data_liquidacao_naive = datetime.strptime(item['data_liquidacao'], '%Y-%m-%d')
                data_liquidacao_aware = timezone.make_aware(data_liquidacao_naive, timezone.get_default_timezone())

                novo_registro = Tabela_realizado.objects.create(
                    fluxo_id=registro_original.id,
                    vencimento=registro_original.vencimento,
                    descricao=registro_original.descricao,
                    observacao=item['observacao'],
                    valor=valor_decimal,
                    conta_contabil=registro_original.conta_contabil,
                    parcela_atual=registro_original.parcela_atual,
                    parcelas_total=registro_original.parcelas_total,
                    tags=registro_original.tags,
                    natureza=registro_original.natureza,
                    original_data_criacao=registro_original.data_criacao,
                    data_liquidacao=data_liquidacao_aware,
                    banco_liquidacao=item.get('banco_liquidacao', '')
                )
                if novo_registro:
                    ids_para_excluir.append(item['id'])
            except ObjectDoesNotExist:
                continue  # Se o objeto não existir, simplesmente continue para o próximo item

        # Exclui os registros originais em Tabela_fluxo
        Tabela_fluxo.objects.filter(id__in=ids_para_excluir).delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'invalid method'}, status=405)


# SIGNAL HANDLERS ############################################################################

@receiver(post_save, sender=Tabela_fluxo)
def save_update_data_unica(sender, instance, **kwargs):
    recalcular_totais()

@receiver(post_delete, sender=Tabela_fluxo)
def delete_update_data_unica(sender, instance, **kwargs):
    recalcular_totais()

def recalcular_totais():
    """ Sinal para atualizar Totais_mes_fluxo quando um FluxoDeCaixa for salvo """
    # Apaga todos os registros existentes em Totais_mes_fluxo
    Totais_mes_fluxo.objects.all().delete()

    # Encontra todas as datas únicas de vencimento em Tabela_fluxo
    datas_unicas = Tabela_fluxo.objects.dates('vencimento', 'month', order='ASC')

    for data_unica in datas_unicas:
        inicio_mes = data_unica
        fim_mes = inicio_mes + relativedelta(months=1, days=-1)

        # Calcula os totais de crédito e débito para cada mês
        total_credito = Tabela_fluxo.objects.filter(
            vencimento__range=(inicio_mes, fim_mes),
            natureza='Crédito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        total_debito = Tabela_fluxo.objects.filter(
            vencimento__range=(inicio_mes, fim_mes),
            natureza='Débito'
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        # Cria um novo registro em Totais_mes_fluxo para cada mês
        Totais_mes_fluxo.objects.create(
            data_formatada=inicio_mes.strftime('%b/%Y'),
            inicio_mes=inicio_mes,
            fim_mes=fim_mes,
            total_credito=total_credito,
            total_debito=total_debito,
            saldo_mensal=total_credito - total_debito
        )

# FUNÇÕES ÚNICAS ############################################################################

def meses_filtro(request):
    totais_mes_fluxo = Totais_mes_fluxo.objects.all().order_by('data_formatada')
    context = {'totais_mes_fluxo': totais_mes_fluxo}
    return render(request, 'fluxo_de_caixa.html', context)

def exibir_bancos(request):
    bancos = Bancos.objects.all()
    return render(request, 'fluxo_de_caixa.html', {'bancos': bancos})
