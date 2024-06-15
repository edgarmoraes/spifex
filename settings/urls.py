from django.urls import path, include
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings, name='settings'),
    path('bancos_e_contas/', views.banks, name='banks'),
    path('departamentos/', views.departments, name='departments'),
    path('estoque/', views.inventory, name='inventory'),
    path('cadastro/', views.entities, name='entities'),
    path('salvar_banco/', views.save_bank, name='save_bank'),
    path('salvar_departamento/', views.save_department, name='save_department'),
    path('salvar_estoque/', views.save_inventory, name='save_inventory'),
    path('salvar_entidade/', views.save_entity, name='save_entity'),
    path('verificar_e_excluir_banco/<int:bank_id>/', views.verify_and_delete_bank, name='verify_and_delete_bank'),
    path('verificar_e_excluir_departamento/<int:department_id>/', views.verify_and_delete_department, name='verify_and_delete_department'),
    path('verificar_e_excluir_estoque/<int:inventory_item_id>/', views.verify_and_delete_inventory, name='verify_and_delete_inventory'),
    path('verificar_e_excluir_entidade/<int:entity_id>/', views.verify_and_delete_entity, name='verify_and_delete_entity'),
]