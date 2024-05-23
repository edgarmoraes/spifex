from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.projects, name='projects'),
    path('salvar_projeto/', views.save_project, name='save_project'),
]