import openpyxl
from django.shortcuts import render, redirect
from .models import ExcelDocument, ExcelData
from .forms import ExcelDocumentForm
from django.db import transaction

def chart_of_accounts(request):
    return render(request, 'chart_of_accounts.html')

def upload_excel_file(request):
    if request.method == 'POST':
        form = ExcelDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():  # Ensure the operation is atomic
                excel_document = form.save()
                workbook = openpyxl.load_workbook(excel_document.excel_file.path, data_only=True)
                worksheet = workbook.active
                for row in worksheet.iter_rows(min_row=2, max_col=3, values_only=True):
                    excel_data_instance = ExcelData(
                        column_a=row[0] or "",
                        column_b=row[1] or "",
                        column_c=row[2] or ""
                    )
                    excel_data_instance.save()  # Save each instance
                    print(f"Saved: {excel_data_instance.column_a}, {excel_data_instance.column_b}, {excel_data_instance.column_c}")  # Debugging line
                # Redirect to a new URL:
                return redirect('display_excel')
        else:
            print(form.errors)  # Print form errors, if any, during debugging
    else:
        form = ExcelDocumentForm()

    return render(request, 'upload_excel.html', {'form': form})

def display_excel(request):
    # Fetch all the rows of data from ExcelData model
    data = ExcelData.objects.all()
    return render(request, 'display_excel.html', {'data': data})