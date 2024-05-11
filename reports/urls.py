from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports, name='reports'),
    path('cash_flow_report/', views.cash_flow_report, name='cash_flow_report'),
]