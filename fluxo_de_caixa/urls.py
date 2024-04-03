from django.urls import path
from . import views

urlpatterns = [
    path('', views.cash_flow, name='cash_flow'),
    path('meses_filtro/', views.filter_months, name='filter_months'),
    path('deletar_entradas/', views.delete_entries, name='filter_months'),
    path('exibir_bancos/', views.display_banks, name='display_banks'),
    path('processar_transferencia/', views.process_transfer, name='process_transfer'),
    path('processar_liquidacao/', views.process_settlement, name='process_settlement'),
]
