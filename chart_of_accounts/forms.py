from django import forms
from .models import ExcelFile

class ExcelFileForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ('excel_file',)