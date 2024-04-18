from django.shortcuts import render
from django.db.models import Sum, Case, When, F, DecimalField
from django.db.models.functions import TruncMonth
from cash_flow.models import CashFlowEntry
from django.http import JsonResponse

def reports(request):
    return render(request, 'reports.html')

def get_monthly_cashflow():
    # Agrupa as entradas por mês e calcula o saldo consolidado
    monthly_data = CashFlowEntry.objects.annotate(
        month=TruncMonth('due_date')
    ).annotate(
        amount_case=Case(
            When(transaction_type='Débito', then=-F('amount')),
            default=F('amount'),
            output_field=DecimalField(max_digits=13, decimal_places=2)
        )
    ).values('month').annotate(
        total=Sum('amount_case')
    ).order_by('month')

    return monthly_data

def cash_flow_report(request):
    data = list(get_monthly_cashflow())
    return render(request, 'cash_flow_report.html', {'data': data})