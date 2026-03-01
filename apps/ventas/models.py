from django.db import models, transaction
from django.db.models import F
from django.conf import settings
from apps.clients.models import Cliente
from apps.productos.models import Producto
from decimal import Decimal

class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
    ]
    
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ventas'
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='cash')
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Relación opcional con Order (solo para modo restaurante)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='sale')
    
    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        app_label = 'ventas'


class DetalleVenta(models.Model):
    """
    Model to store sale item details
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalleventa_set')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
   
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class Order(models.Model):
    """
    Modelo para pedidos en modo restaurante.
    Separado de Venta para mantener arquitectura limpia.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PREPARING', 'En Preparación'),
        ('READY', 'Listo'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    # Relación con el negocio (multi-tenant)
    business = models.ForeignKey(
        'usuarios.Business',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # Número de orden secuencial por negocio
    order_number = models.PositiveIntegerField()
    
    # Estado del pedido
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Timestamps para tracking
    created_at = models.DateTimeField(auto_now_add=True)
    preparing_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Notas adicionales
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = 'ventas'
        ordering = ['-created_at']
        unique_together = [['business', 'order_number']]
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['business', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Orden #{self.order_number} - {self.get_status_display()}"
    
    def get_items(self):
        """Obtiene los items de la venta asociada"""
        try:
            # La relación es order.sale (reverse ForeignKey desde Venta)
            # sale es un RelatedManager, no un QuerySet directo
            venta = self.sale.first()
            if venta:
                return venta.detalleventa_set.all()
        except Exception as e:
            print(f"Error getting items for order {self.id}: {e}")
        return []
    
    def get_elapsed_time(self):
        """Calcula el tiempo transcurrido desde la creación"""
        from django.utils import timezone
        elapsed = timezone.now() - self.created_at
        minutes = int(elapsed.total_seconds() / 60)
        return f"{minutes} min"
