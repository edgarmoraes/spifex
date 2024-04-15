from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('home/', views.HomePage, name='home'),
    path('signup/', views.SignupPage, name='signup'),
    path('login/', views.LoginPage, name='login'),
]