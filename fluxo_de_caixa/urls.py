from django.urls import path
from . import views

urlpatterns = [
    path('', views.fluxo_de_caixa),
    path('meses_filtro/', views.meses_filtro, name='meses_filtro'),
    path('deletar-entradas/', views.deletar_entradas, name='deletar-entradas'),
    path('filtrar-lancamentos/', views.filtrar_lancamentos, name='filtrar_lancamentos'),
]
