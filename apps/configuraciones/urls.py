from django.urls import path
from . import views

app_name = 'configuraciones'

urlpatterns = [
    path('', views.index, name='index'),
    path('business/', views.business_config, name='business_config'),
    path('personalizacion/', views.personalizacion, name='personalizacion'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('sistema/', views.sistema, name='sistema'),
    path('obtener-empresa-json/', views.obtener_empresa_json, name='obtener_empresa_json'),
    # Add this to your existing URL patterns
    path('cuenta/', views.cuenta, name='cuenta'),
]