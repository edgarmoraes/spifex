from django.urls import path
from . import views

urlpatterns = [
    path('', views.chart_of_accounts, name='chart_of_accounts'),
    path('upload/', views.upload_excel_file, name='upload_excel'),
    path('display/', views.display_excel, name='display_excel'),
]