from django.shortcuts import render

def configuracoes(request):
    if request.method =="GET":
        return render(request, 'configuracoes.html')