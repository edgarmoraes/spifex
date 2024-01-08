from django.urls import path
from . import views

urlpatterns = [
    path('', views.fluxo_de_caixa),
]
