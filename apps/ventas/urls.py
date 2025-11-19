from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.ventas, name='ventas'),
    path('completar/', views.completar_venta, name='completar_venta'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('venta-completa/<int:venta_id>/', views.venta_completa, name='venta_completa'),
    # Add a URL pattern without venta_id parameter
    path('venta/completa/', views.venta_completa_sin_id, name='venta_completa_sin_id'),
    # Add the missing URL patterns
    path('venta/<int:venta_id>/descargar/', views.descargar_factura, name='descargar_factura'),
    path('nueva/', views.ventas, name='nueva_venta'),  # This just redirects to the ventas page
    # Add this to your urlpatterns
    path('verificar-stock/', views.verificar_stock, name='verificar_stock'),
    # Add this to your existing URL patterns
    path('actualizar-cliente/<int:venta_id>/', views.actualizar_cliente_venta, name='actualizar_cliente_venta'),
    # Add the cashier interface URL
    path('cajero/', views.ventas_cajero, name='ventas_cajero'),
]