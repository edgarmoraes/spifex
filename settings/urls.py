from django.urls import path, include
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings, name='settings'),
    path('bancos_e_contas/', views.banks, name='banks'),
    path('departamentos/', views.departments, name='departments'),
    path('salvar_banco/', views.save_bank, name='save_bank'),
    path('salvar_departamento/', views.save_department, name='save_department'),
    path('verificar_e_excluir_banco/<int:bank_id>/', views.verify_and_delete_bank, name='verify_and_delete_bank'),
    path('verificar_e_excluir_departamento/<int:department_id>/', views.verify_and_delete_department, name='verify_and_delete_department'),
]