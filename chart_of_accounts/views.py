import openpyxl
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Chart_of_accounts
from .forms import AccountForm
from django.http import JsonResponse
from django.contrib import messages

def upload_and_save(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            worksheet = wb.active

            # Verificar as células especiais
            if (worksheet['XFD1'].value != "sppiff" or
                worksheet['XFD2'].value != "1ccd101b-aed4-4b56-b852-02c8ce8a6f70" or
                worksheet['XFD3'].value != "a5296f55-e314-48d2-8415-f0204d3162f8"):
                messages.error(request, 'A planilha não passou na verificação de segurança.')
                return redirect('/plano_de_contas/')  # Substitua pelo nome da URL de upload

            Chart_of_accounts.objects.all().delete()  # Apaga todos os registros existentes
            
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

    
    else:
        form = UploadFileForm()
    
    chart_of_accounts = Chart_of_accounts.objects.all().order_by('-group')
    return render(request, 'chart_of_accounts.html', {'form': form, 'chart_of_accounts': chart_of_accounts})

def verify_special_cells(worksheet):
    expected_values = {
        'XFD1': "sppiff",
        'XFD2': "1ccd101b-aed4-4b56-b852-02c8ce8a6f70",
        'XFD3': "a5296f55-e314-48d2-8415-f0204d3162f8"
    }
    for cell, expected_value in expected_values.items():
        actual_value = worksheet[cell].value
        if actual_value != expected_value:
            return False
    return True

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
    groups = request.GET.get('group')
    groups = Chart_of_accounts.objects.values_list('group', flat=True)\
                                      .distinct()
    return JsonResponse(list(groups), safe=False)

def get_subgroups(request):
    group = request.GET.get('group')
    subgroups = Chart_of_accounts.objects.filter(group=group).values_list('subgroup', flat=True).distinct()
    return JsonResponse(list(subgroups), safe=False)