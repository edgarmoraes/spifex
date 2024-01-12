from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from .models import Tabela_fluxo, TabelaTemporaria

def fluxo_de_caixa(request):
    if request.method == "GET":
        # Retrieve all recebimentos objects from the database
        Tabela_fluxo_list = Tabela_fluxo.objects.all()
        
        # Pass the data to the template context
        context = {'Tabela_fluxo_list': Tabela_fluxo_list}
        return render(request, 'fluxo_de_caixa.html', context)
    elif request.method == "POST":
        vencimento = request.POST.get('vencimento')
        descricao = request.POST.get('descricao')
        observacao = request.POST.get('observacao')
        valor = request.POST.get('valor')
        conta_contabil = request.POST.get('conta_contabil')
        parcelas = request.POST.get('parcelas')
        tags = request.POST.get('tags')
        if 'salvar_recebimento' in request.POST:
            natureza = 'Crédito'
        else: natureza = 'Débito'

        vencimento = datetime.strptime(vencimento, '%Y-%m-%d')  # Ajuste o formato conforme necessário
        parcelas = int(parcelas)

        for i in range(parcelas):
            vencimento_parcela = vencimento + timedelta(days=30 * i)
            fluxo_de_caixa = Tabela_fluxo(
                vencimento=vencimento_parcela,
                descricao=descricao,
                observacao=observacao,
                valor=valor,
                conta_contabil=conta_contabil,
                parcelas=str(i+1) + '/' + str(parcelas),
                tags=tags,
                natureza=natureza,
                data_criacao=datetime.now(),
            )
            fluxo_de_caixa.save()

        return redirect(request.path)


        fluxo_de_caixa = Tabela_fluxo(
            vencimento=vencimento,
            descricao=descricao,
            observacao=observacao,
            valor=valor,
            conta_contabil=conta_contabil,
            parcelas=parcelas,
            tags=tags,
            natureza=natureza,
            data_criacao=datetime.now(),
        )

        fluxo_de_caixa.save()

        return redirect(request.path)
    
@csrf_exempt
def deletar_entradas(request):
    if request.method == 'POST':
        # Lendo o corpo da solicitação como JSON
        data = json.loads(request.body)
        ids_para_apagar = data.get('ids')

        # Processando cada ID
        for id_str in ids_para_apagar:
            id = int(id_str)  # Convertendo o ID para inteiro
            try:
                # Buscando o objeto na Tabela_fluxo
                objeto = Tabela_fluxo.objects.get(id=id)

                # Criando um novo objeto na TabelaTemporaria
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

                # Apagando o objeto original
                objeto.delete()

            except Tabela_fluxo.DoesNotExist:
                # O ID não foi encontrado na Tabela_fluxo
                continue

        # Responder ao frontend
        return JsonResponse({'status': 'success'})
    
@require_POST
def atualizar_lancamento(request):
    # Obter dados do formulário
    lancamento_id = request.POST.get('id')
    novo_valor = request.POST.get('valor')
    tipo = request.POST.get('tipo')  # débito ou crédito

    # Atualizar o lançamento no banco de dados
    # ...

    return JsonResponse({'status': 'sucesso'})