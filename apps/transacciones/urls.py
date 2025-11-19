from django.urls import path
from . import views

app_name = 'transacciones'

urlpatterns = [
    path('', views.lista_transacciones, name='lista_transacciones'),
    path('<int:transaccion_id>/', views.detalle_transaccion, name='detalle_transaccion'),
    path('buscar/', views.buscar_transacciones, name='buscar_transacciones'),
]