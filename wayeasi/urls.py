from django.contrib import admin
from django.urls import path, include
from registration import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fluxo_de_caixa/', include(('fluxo_de_caixa.urls', 'fluxo_de_caixa'), namespace='fluxo_de_caixa')),
    path('realizado/', include(('realizado.urls', 'realizado'), namespace='realizado')),
    path('configuracoes/', include(('configuracoes.urls', 'configuracoes'), namespace='configuracoes')),
    # Remove plano_de_contas from here if it's supposed to be under configuracoes
    path('accounts/', include('registration.urls')),
    path('home/', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),
]