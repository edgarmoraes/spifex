from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_and_save, name='plano_de_contas'),
]