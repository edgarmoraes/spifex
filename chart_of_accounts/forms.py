from django import forms
from .models import Chart_of_accounts

class UploadFileForm(forms.Form):
    file = forms.FileField()

class AccountForm(forms.ModelForm):
    class Meta:
        model = Chart_of_accounts
        fields = ['group', 'subgroup', 'account']