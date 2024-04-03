from django.urls import path
from . import views

app_name = 'chart_of_accounts'

urlpatterns = [
    path('', views.chart_of_accounts, name='chart_of_accounts'),
    path('adicionar-conta/', views.add_account, name='adicionar_conta'),
    path('get-groups/', views.get_groups, name='get_groups'),
    path('get-subgroups/', views.get_subgroups, name='get_subgroups'),
    path('editar-conta/<int:account_id>/', views.edit_account, name='edit_account'),
    path('delete-account/<int:account_id>/', views.delete_account, name='delete_account'),
]