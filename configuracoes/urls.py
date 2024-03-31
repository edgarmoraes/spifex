from django.urls import path, include
from . import views

app_name = 'configuracoes'

urlpatterns = [
    path('', views.configuracoes, name='configuracoes'),
    path('bancos_e_contas/', views.bancos_e_contas, name='bancos_e_contas'),
    path('departamentos/', views.departments, name='departments'),
    path('salvar_banco/', views.salvar_banco, name='salvar_banco'),
    path('salvar_departamento/', views.salvar_departamento, name='salvar_departamento'),
    path('verificar_e_excluir_banco/<int:idBanco>/', views.verificar_e_excluir_banco, name='verificar_e_excluir_banco'),
]