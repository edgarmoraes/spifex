from django.contrib import admin
from django.urls import path, include
from registration import views
from chart_of_accounts.views import chart_of_accounts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fluxo_de_caixa/', include(('fluxo_de_caixa.urls', 'cash_flow'), namespace='cash_flow')),
    path('realizado/', include(('realizado.urls', 'settled_entry'), namespace='settled_entry')),
    path('configuracoes/', include(('configuracoes.urls', 'settings'), namespace='settings')),
    path('accounts/', include('registration.urls')),
    path('home/', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),
    path('configuracoes/plano_de_contas/', include(('chart_of_accounts.urls', 'chart_of_accounts'), namespace='chart_of_accounts')),
]