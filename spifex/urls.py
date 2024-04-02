from django.contrib import admin
from django.urls import path, include
from registration import views
from chart_of_accounts.views import upload_and_save

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fluxo_de_caixa/', include(('fluxo_de_caixa.urls', 'fluxo_de_caixa'), namespace='fluxo_de_caixa')),
    path('realizado/', include(('realizado.urls', 'realizado'), namespace='realizado')),
    path('configuracoes/', include(('configuracoes.urls', 'configuracoes'), namespace='configuracoes')),
    path('accounts/', include('registration.urls')),
    path('home/', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),
    path('plano_de_contas/', include(('chart_of_accounts.urls', 'chart_of_accounts'), namespace='plano_de_contas')),
]