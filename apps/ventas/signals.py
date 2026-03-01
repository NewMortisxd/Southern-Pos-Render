"""
Señales para el módulo de ventas.
Implementa Event-Driven Architecture para notificaciones en tiempo real.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order, Venta


@receiver(post_save, sender=Order)
def order_changed(sender, instance, created, **kwargs):
    """
    Señal que se dispara cuando se crea o actualiza una orden.
    Envía notificación WebSocket a todos los clientes conectados.
    """
    channel_layer = get_channel_layer()
    room_group_name = f'orders_{instance.business.id}'
    
    # Preparar datos de la orden
    order_data = {
        'id': instance.id,
        'order_number': instance.order_number,
        'status': instance.status,
        'status_display': instance.get_status_display(),
        'created_at': instance.created_at.isoformat(),
        'elapsed_time': instance.get_elapsed_time(),
        'notes': instance.notes or '',
    }
    
    # Agregar items si existe venta asociada
    items = []
    try:
        # Usar get_items() que maneja correctamente la relación
        for detalle in instance.get_items():
            items.append({
                'producto': detalle.producto.nombre,
                'cantidad': detalle.cantidad,
            })
        order_data['items'] = items
    except Exception as e:
        print(f"Error getting items in signal: {e}")
        order_data['items'] = []
    
    # Determinar tipo de evento
    event_type = 'order_created' if created else 'order_status_changed'
    
    # Enviar mensaje al grupo
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': event_type,
                'data': order_data
            }
        )



@receiver(post_save, sender=Venta)
def venta_saved(sender, instance, created, **kwargs):
    """
    Señal que se dispara cuando se guarda una venta.
    Si la venta tiene una orden asociada, notifica el cambio para actualizar los items.
    """
    if instance.order:
        # Disparar la señal de order_changed para actualizar los items
        channel_layer = get_channel_layer()
        room_group_name = f'orders_{instance.order.business.id}'
        
        # Preparar datos de la orden con items actualizados
        order_data = {
            'id': instance.order.id,
            'order_number': instance.order.order_number,
            'status': instance.order.status,
            'status_display': instance.order.get_status_display(),
            'created_at': instance.order.created_at.isoformat(),
            'elapsed_time': instance.order.get_elapsed_time(),
            'notes': instance.order.notes or '',
        }
        
        # Agregar items
        items = []
        try:
            for detalle in instance.detalleventa_set.all():
                items.append({
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                })
            order_data['items'] = items
        except Exception as e:
            print(f"Error getting items in venta signal: {e}")
            order_data['items'] = []
        
        # Enviar mensaje al grupo (siempre como order_status_changed para actualizar)
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'order_status_changed',
                    'data': order_data
                }
            )
