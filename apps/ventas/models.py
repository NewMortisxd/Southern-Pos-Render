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