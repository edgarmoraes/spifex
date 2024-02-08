from django.urls import path
from . import views

app_name = 'realizado'

urlpatterns = [
    path('', views.realizado, name='realizado'),
    path('meses_filtro_realizado/', views.meses_filtro_realizado, name='meses_filtro_realizado'),
    path('processar_liquidacao/', views.processar_liquidacao, name='processar_liquidacao'),
    path('processar_retorno/', views.processar_retorno, name='processar_retorno'),
]
