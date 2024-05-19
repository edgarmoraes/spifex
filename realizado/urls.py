from django.urls import path
from . import views

app_name = 'realizado'

urlpatterns = [
    path('', views.settled_entry, name='settled_entry'),
    path('meses_filtro_realizado/', views.filter_months_settled, name='filter_months_settled'),
    path('processar_retorno/', views.process_return, name='process_return'),
    path('atualizar-lancamento/<int:id>/', views.update_entry, name='update_entry'),
    path('atualizar-lancamentos-uuid/<str:uuid_transference>/', views.update_entries_by_uuid, name='update_entries_by_uuid'),
]
