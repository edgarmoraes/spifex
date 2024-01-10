from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render
from .models import Tabela_fluxo

# Create your views here.
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
    
    