from django.shortcuts import render, redirect
from .models import ExcelFile
from .forms import ExcelFileForm
import openpyxl

def chart_of_accounts(request):
    return render(request, 'chart_of_accounts.html')

def upload_and_show_excel(request):
    if request.method == 'POST':
        form = ExcelFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('display_excel')
    else:
        form = ExcelFileForm()
    return render(request, 'upload_excel.html', {'form': form})

def display_excel(request):
    excel_file = ExcelFile.objects.last()
    workbook = openpyxl.load_workbook(excel_file.excel_file.path)
    worksheet = workbook.active
    data = []
    for row in worksheet.iter_rows(values_only=True, max_col=3):
        data.append(row)
    return render(request, 'display_excel.html', {'data': data})