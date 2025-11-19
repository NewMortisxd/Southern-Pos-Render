from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Vista principal de reportes
    path('', views.reportes_view, name='index'),
    
    # Reportes Financieros y Fiscales
    path('ventas/', views.ventas, name='ventas'),
    path('iva/', views.iva_report, name='iva'),
    path('facturas/', views.facturas_report, name='facturas'),
    
    # Reportes para el SRI
    path('ventas/', views.ventas, name='ventas'),
    path('iva-declaracion/', views.iva_declaracion, name='iva_declaracion'),
    path('ats/', views.ats, name='ats'),
    path('renta/', views.renta_report, name='renta'),  # Added missing URL pattern
    
    # Reportes Operativos
    path('inventario/', views.inventario_report, name='inventario'),
    path('analisis-ventas/', views.analisis_ventas_report, name='analisis_ventas'),
    path('clientes/', views.clientes_report, name='clientes'),
    
    # Reportes Rápidos
    path('ventas-diarias/', views.ventas_diarias_report, name='ventas_diarias'),
    path('productos-top/', views.productos_top_report, name='productos_top'),
    path('stock-bajo/', views.stock_bajo_report, name='stock_bajo'),
    path('generar-xml/', views.generar_xml, name='generar_xml'),
]