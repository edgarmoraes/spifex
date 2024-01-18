from django.urls import path
from . import views

urlpatterns = [
    path('', views.fluxo_de_caixa),
    path('meses_filtro/', views.meses_filtro, name='meses_filtro'),
    path('bancos_filtro/', views.bancos_filtro, name='bancos_filtro'),
    path('deletar_entradas/', views.deletar_entradas, name='deletar_entradas'),
    path('filtrar_lancamentos/', views.filtrar_lancamentos, name='filtrar_lancamentos'),
    path('exibir_bancos/', views.exibir_bancos, name='exibir_bancos'),
]
