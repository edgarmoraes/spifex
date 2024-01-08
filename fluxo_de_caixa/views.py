from django.shortcuts import render
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

        recebimento = recebimentos(
            vencimento=vencimento,
            descricao=descricao,
            data_criacao=datetime.now()
        )

        recebimento.save()

        return render(request, 'fluxo_de_caixa.html')