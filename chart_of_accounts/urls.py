from django.urls import path
from . import views

app_name = 'chart_of_accounts'

urlpatterns = [
    path('', views.upload_and_save, name='plano_de_contas'),
    path('adicionar-conta/', views.add_account, name='adicionar-conta'),
    path('get-groups/', views.get_groups, name='get-groups'),
    path('get-subgroups/', views.get_subgroups, name='get-subgroups'),
]