from django.urls import path
from . import views

urlpatterns = [
    path('', views.fluxo_de_caixa),
    path('deletar-entradas/', views.deletar_entradas, name='deletar-entradas'),
]
