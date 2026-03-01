"""
URLs para Kitchen Display System (KDS) y Pantalla Pública
"""
from django.urls import path
from . import views_kds

app_name = 'kds'

urlpatterns = [
    # KDS Views
    path('kitchen/', views_kds.kds_view, name='kds'),
    path('kitchen/orders/', views_kds.kds_orders_json, name='kds_orders_json'),
    path('kitchen/order/<int:order_id>/update/', views_kds.kds_update_status, name='kds_update_status'),
    
    # Public Display Views
    path('display/', views_kds.public_display_view, name='public_display'),
    path('display/orders/', views_kds.display_orders_json, name='display_orders_json'),
]
