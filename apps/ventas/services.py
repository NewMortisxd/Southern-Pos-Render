"""
Servicios de negocio para el módulo de ventas.
Contiene lógica de negocio relacionada con órdenes y ventas.
"""
from django.utils import timezone
from django.db import transaction
from .models import Order


class OrderService:
    """Servicio para gestión de órdenes"""
    
    @staticmethod
    def get_active_orders(business):
        """
        Obtiene órdenes activas (PENDING, PREPARING, READY) para un negocio.
        """
        return Order.objects.filter(
            business=business,
            status__in=['PENDING', 'PREPARING', 'READY']
        ).select_related('business').prefetch_related('sale__detalleventa_set__producto').order_by('created_at')
    
    @staticmethod
    def get_ready_orders(business):
        """
        Obtiene órdenes listas (READY) para un negocio.
        """
        return Order.objects.filter(
            business=business,
            status='READY'
        ).select_related('business').order_by('ready_at')
    
    @staticmethod
    @transaction.atomic
    def update_order_status(order_id, new_status):
        """
        Actualiza el estado de una orden y registra el timestamp correspondiente.
        """
        order = Order.objects.select_for_update().get(id=order_id)
        order.status = new_status
        
        # Actualizar timestamps según el nuevo estado
        now = timezone.now()
        if new_status == 'PREPARING':
            order.preparing_at = now
        elif new_status == 'READY':
            order.ready_at = now
        elif new_status == 'DELIVERED':
            order.delivered_at = now
        elif new_status == 'CANCELLED':
            order.cancelled_at = now
        
        order.save()
        return order
    
    @staticmethod
    def create_order_number(business):
        """
        Genera el siguiente número de orden secuencial para un negocio.
        """
        last_order = Order.objects.filter(business=business).order_by('-order_number').first()
        if last_order:
            return last_order.order_number + 1
        return 1
    
    @staticmethod
    def should_create_order(business):
        """
        Determina si se debe crear una orden para una venta.
        Retorna True si el negocio tiene habilitado el sistema de órdenes.
        """
        return business.supports_orders() if hasattr(business, 'supports_orders') else False
    
    @staticmethod
    @transaction.atomic
    def create_order_for_sale(sale, business):
        """
        Crea una orden asociada a una venta.
        """
        order_number = OrderService.create_order_number(business)
        order = Order.objects.create(
            business=business,
            order_number=order_number,
            status='PENDING'
        )
        
        # Asociar la venta con la orden
        sale.order = order
        sale.save()
        
        return order
