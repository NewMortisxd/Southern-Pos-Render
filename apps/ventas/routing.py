"""
WebSocket routing para el módulo de ventas.
Define las rutas WebSocket para actualizaciones en tiempo real de órdenes.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<business_id>\w+)/$', consumers.OrderConsumer.as_asgi()),
]
