import openpyxl
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Chart_of_accounts
from .forms import AccountForm
from django.http import JsonResponse

def upload_and_save(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            Chart_of_accounts.objects.all().delete()  # Apaga todos os registros existentes
            excel_file = request.FILES['file']
            wb = openpyxl.load_workbook(excel_file)
            worksheet = wb.active
            
            # Criar um objeto para cada linha na planilha
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                if row[1] is None:
                    continue
                Chart_of_accounts.objects.create(
                    nature=row[0] or '',
                    group=row[1] or '',
                    subgroup=row[2] or '',
                    account=row[3] or ''
                )
            
            # Adicionar as duas linhas especiais ao final
            Chart_of_accounts.objects.create(
                nature='Crédito',
                group='Transferência entre Contas',
                subgroup='Operação Nula',
                account='Transferência Entrada'
            )
            Chart_of_accounts.objects.create(
                nature='Débito',
                group='Transferência entre Contas',
                subgroup='Operação Nula',
                account='Transferência Saída'
            )
    
    else:
        form = UploadFileForm()
    
    chart_of_accounts = Chart_of_accounts.objects.all().order_by('-group')
    return render(request, 'chart_of_accounts.html', {'form': form, 'chart_of_accounts': chart_of_accounts})

def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plano_de_contas')
    else:
        form = AccountForm()
    return render(request, 'add_account_form.html', {'form': form})

def get_groups(request):
    # Filtrar os grupos excluindo 'Transferência entre Contas'
    groups = Chart_of_accounts.objects.exclude(group='Transferência entre Contas')\
                                      .values_list('group', flat=True)\
                                      .distinct()
    return JsonResponse(list(groups), safe=False)

def get_subgroups(request):
    group = request.GET.get('group')
    subgroups = Chart_of_accounts.objects.filter(group=group).values_list('subgroup', flat=True).distinct()
    return JsonResponse(list(subgroups), safe=False)