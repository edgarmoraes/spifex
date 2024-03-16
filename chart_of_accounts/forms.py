from django import forms
from .models import ExcelDocument

class ExcelDocumentForm(forms.ModelForm):
    class Meta:
        model = ExcelDocument
        fields = ('excel_file',)
