from django.urls import path
from . import views

app_name = 'realizado'

urlpatterns = [
    path('', views.realizado, name='realizado'),
]
