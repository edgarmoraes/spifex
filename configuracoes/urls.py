from django.urls import path
from . import views

app_name = 'configuracoes'

urlpatterns = [
    path('', views.configuracoes, name='configuracoes'),
    path('bancos_e_contas/', views.bancos_e_contas, name='bancos_e_contas'),
    path('salvar_banco/', views.salvar_banco, name='salvar_banco'),
]