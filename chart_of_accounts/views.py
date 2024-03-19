import openpyxl
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Chart_of_accounts

def upload_and_save(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            Chart_of_accounts.objects.all().delete()  # Apaga todos os registros existentes
            excel_file = request.FILES['file']
            wb = openpyxl.load_workbook(excel_file)
            worksheet = wb.active
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                Chart_of_accounts.objects.create(
                    column1=row[0],
                    column2=row[1],
                    column3=row[2],
                    column4=row[3]
                )
    else:
        form = UploadFileForm()
    
    chart_of_accounts = Chart_of_accounts.objects.all().order_by('-column2')
    return render(request, 'chart_of_accounts.html', {'form': form, 'chart_of_accounts': chart_of_accounts})
