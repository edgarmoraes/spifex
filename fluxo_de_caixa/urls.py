from django.urls import path
from . import views

urlpatterns = [
    path('', views.cash_flow, name='cash_flow'),
    path('meses_filtro/', views.filter_months_cash_flow, name='filter_months_cash_flow'),
    path('deletar_entradas/', views.delete_entries, name='delete_entries'),
    path('exibir_bancos/', views.display_banks, name='display_banks'),
    path('processar_transferencia/', views.process_transfer, name='process_transfer'),
    path('processar_liquidacao/', views.process_settlement, name='process_settlement'),
]
