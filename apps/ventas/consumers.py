"""
WebSocket consumers para actualizaciones en tiempo real de órdenes.
Implementa Event-Driven Architecture para notificaciones instantáneas.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class OrderConsumer(AsyncWebsocketConsumer):
    """
    Consumer para actualizaciones de órdenes en tiempo real.
    Maneja conexiones WebSocket para KDS y pantalla pública.
    """
    
    async def connect(self):
        """Maneja la conexión WebSocket"""
        self.business_id = self.scope['url_route']['kwargs']['business_id']
        self.room_group_name = f'orders_{self.business_id}'
        
        # Verificar autenticación
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close()
            return
        
        # Verificar que el usuario pertenece al negocio
        has_access = await self.check_business_access(user, self.business_id)
        if not has_access:
            await self.close()
            return
        
        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Maneja la desconexión WebSocket"""
        # Salir del grupo de la sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recibe mensajes del WebSocket (no usado en este caso)"""
        pass
    
    async def order_update(self, event):
        """
        Recibe actualizaciones de órdenes desde el grupo y las envía al cliente.
        """
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'data': event['data']
        }))
    
    async def order_created(self, event):
        """Notifica cuando se crea una nueva orden"""
        await self.send(text_data=json.dumps({
            'type': 'order_created',
            'data': event['data']
        }))
    
    async def order_status_changed(self, event):
        """Notifica cuando cambia el estado de una orden"""
        await self.send(text_data=json.dumps({
            'type': 'order_status_changed',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def check_business_access(self, user, business_id):
        """Verifica que el usuario tenga acceso al negocio"""
        from apps.usuarios.models import Business
        try:
            business = Business.objects.get(id=business_id, user=user)
            return True
        except Business.DoesNotExist:
            return False
