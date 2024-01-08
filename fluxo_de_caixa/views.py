from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import recebimentos
from datetime import datetime

# Create your views here.
def fluxo_de_caixa(request):
    if request.method == "GET":
        return render(request, 'fluxo_de_caixa.html')
    elif request.method == "POST":
        vencimento = request.POST.get('vencimento')
        descricao = request.POST.get('descricao')
        observacao = request.POST.get('observacao')
        valor = request.POST.get('valor')
        conta_contabil = request.POST.get('conta_contabil')
        parcelas = request.POST.get('parcelas')
        tags = request.POST.get('tags')

        recebimento = recebimentos(
            vencimento=vencimento,
            descricao=descricao,
            observacao=observacao,
            valor=valor,
            conta_contabil=conta_contabil,
            parcelas=parcelas,
            tags=tags,
            data_criacao=datetime.now(),
        )

        recebimento.save()

        return redirect(request.path)