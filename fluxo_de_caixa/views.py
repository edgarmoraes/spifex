from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render
from .models import recebimentos

# Create your views here.
def fluxo_de_caixa(request):
    if request.method == "GET":
        # Retrieve all recebimentos objects from the database
        recebimentos_list = recebimentos.objects.all()
        
        # Pass the data to the template context
        context = {'recebimentos_list': recebimentos_list}
        return render(request, 'fluxo_de_caixa.html', context)
    elif request.method == "POST":
        vencimento = request.POST.get('vencimento')
        descricao = request.POST.get('descricao')
        observacao = request.POST.get('observacao')
        valor = request.POST.get('valor')
        conta_contabil = request.POST.get('conta_contabil')
        parcelas = request.POST.get('parcelas')
        tags = request.POST.get('tags')

        natureza = 'Crédito'  # Valor padrão

        # Verificar o botão submit
        submit_button = request.POST.get('submit_button')
        if submit_button == 'salvar_pagamento':
            natureza = 'Débito'

        recebimento = recebimentos(
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

        recebimento.save()

        return redirect(request.path)
    
    