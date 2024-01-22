from django.urls import path
from . import views

urlpatterns = [
    path('', views.fluxo_de_caixa, name='fluxo_de_caixa'),
    path('meses_filtro/', views.meses_filtro, name='meses_filtro'),
    path('deletar_entradas/', views.deletar_entradas, name='deletar_entradas'),
    path('exibir_bancos/', views.exibir_bancos, name='exibir_bancos'),
]
