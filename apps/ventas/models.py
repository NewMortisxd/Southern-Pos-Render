from django.db import models, transaction
from django.db.models import F
from django.conf import settings
from apps.clients.models import Cliente
from apps.productos.models import Producto
from decimal import Decimal
from django.core.validators import RegexValidator


class PuntoEmision(models.Model):
    """
    Modelo para puntos de emisión de facturas.
    Cada punto de emisión tiene su propio secuencial independiente.
    
    Ejemplos:
    - Caja 1: 001-001 (establecimiento 001, punto 001)
    - Caja 2: 001-002 (establecimiento 001, punto 002)
    - Sucursal B: 002-001 (establecimiento 002, punto 001)
    """
    
    # Validador para códigos de 3 dígitos
    codigo_validator = RegexValidator(
        regex=r'^\d{3}$',
        message='El código debe ser exactamente 3 dígitos numéricos (ej: 001, 002)'
    )
    
    business = models.ForeignKey(
        'usuarios.Business',
        on_delete=models.CASCADE,
        related_name='puntos_emision',
        verbose_name='Negocio'
    )
    
    codigo = models.CharField(
        max_length=3,
        validators=[codigo_validator],
        verbose_name='Código Punto Emisión',
        help_text='3 dígitos (ej: 001, 002)'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Ej: Caja 1, Caja Principal, Sucursal Norte'
    )
    
    establecimiento_codigo = models.CharField(
        max_length=3,
        validators=[codigo_validator],
        verbose_name='Código Establecimiento',
        help_text='3 dígitos (ej: 001)'
    )
    
    secuencial_actual = models.PositiveIntegerField(
        default=1,
        verbose_name='Secuencial Actual',
        help_text='Se autoincrementa con cada factura. NO modificar manualmente.'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Punto de Emisión'
        verbose_name_plural = 'Puntos de Emisión'
        ordering = ['establecimiento_codigo', 'codigo']
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'establecimiento_codigo', 'codigo'],
                name='unique_punto_emision_por_negocio'
            )
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.establecimiento_codigo}-{self.codigo})"
    
    def get_numero_factura_formato(self):
        """Retorna el formato del número de factura para este punto"""
        return f"{self.establecimiento_codigo}-{self.codigo}-{self.secuencial_actual:09d}"
    
    def delete(self, *args, **kwargs):
        """
        🚨 PROTECCIÓN: No permitir eliminación física si tiene ventas.
        En su lugar, desactivar el punto de emisión.
        """
        from apps.ventas.models import Venta
        
        # Verificar si tiene ventas
        if Venta.objects.filter(punto_emision=self).exists():
            # No eliminar, solo desactivar
            self.activo = False
            self.save(update_fields=['activo'])
            
            # Log de auditoría
            import logging
            logger = logging.getLogger('facturacion')
            logger.warning(
                f'INTENTO DE ELIMINACIÓN BLOQUEADO - PuntoEmision: {self.id}, '
                f'Business: {self.business.nombre_negocio}, '
                f'Código: {self.establecimiento_codigo}-{self.codigo}, '
                f'Acción: Desactivado en vez de eliminado'
            )
            return
        
        # Si no tiene ventas, permitir eliminación
        super().delete(*args, **kwargs)
    
    @transaction.atomic
    def generar_numero_factura(self):
        """
        Genera el próximo número de factura y actualiza el secuencial.
        Usa select_for_update para prevenir race conditions.
        
        Returns:
            tuple: (establecimiento, punto_emision, secuencial, numero_completo)
        """
        # Recargar con lock
        punto = PuntoEmision.objects.select_for_update().get(pk=self.pk)
        
        establecimiento = punto.establecimiento_codigo
        codigo_punto = punto.codigo
        secuencial = punto.secuencial_actual
        
        # Generar número completo
        numero_factura = f"{establecimiento}-{codigo_punto}-{secuencial:09d}"
        
        # Incrementar secuencial
        punto.secuencial_actual = F('secuencial_actual') + 1
        punto.save(update_fields=['secuencial_actual'])
        
        # 🔥 Refrescar para tener el valor actualizado
        punto.refresh_from_db()
        
        # 🔥 AUDITORÍA: Registrar generación de factura
        import logging
        logger = logging.getLogger('facturacion')
        logger.info(
            f'FACTURA GENERADA - PuntoEmision: {self.id}, '
            f'Número: {numero_factura}, '
            f'Nuevo secuencial: {punto.secuencial_actual}'
        )
        
        return establecimiento, codigo_punto, secuencial, numero_factura


class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('credit', 'Crédito'),  # Agregado para ventas a crédito
    ]
    
    ESTADO_SRI_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('AUTORIZADA', 'Autorizada'),
        ('RECHAZADA', 'Rechazada'),
        ('NO_AUTORIZADA', 'No Autorizada'),
    ]
    
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('parcial', 'Pago Parcial'),
        ('pagado', 'Pagado Completo'),
    ]
    
    TIPO_COMPROBANTE_CHOICES = [
        ('ticket', 'Ticket'),
        ('factura', 'Factura Electrónica'),
        ('nota_venta', 'Nota de Venta'),
    ]
    
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ventas'
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    # === SESIÓN DE CAJA ===
    caja_sesion = models.ForeignKey(
        'CajaSesion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas',
        verbose_name='Sesión de Caja',
        help_text='Sesión de caja en la que se realizó esta venta'
    )
    
    # === TOTALES ===
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento Total")
    recargo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Recargo Total")
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # === PAGO ===
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='cash')
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # === ESTADO DE PAGO ===
    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO_CHOICES,
        default='pagado',
        verbose_name="Estado de Pago"
    )
    saldo_pendiente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Saldo Pendiente"
    )
    
    # === TIPO DE COMPROBANTE ===
    tipo_comprobante = models.CharField(
        max_length=20,
        choices=TIPO_COMPROBANTE_CHOICES,
        default='ticket',
        verbose_name="Tipo de Comprobante"
    )
    
    # Relación opcional con Order (solo para modo restaurante)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='sale')
    
    # 🎯 Relación con Punto de Emisión (NUEVO - Arquitectura mejorada)
    punto_emision = models.ForeignKey(
        'PuntoEmision',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ventas',
        verbose_name='Punto de Emisión',
        help_text='Punto de emisión que generó esta factura'
    )
    
    # 🎯 FACTURACIÓN ELECTRÓNICA SRI
    establecimiento_codigo = models.CharField(
        max_length=3,
        default='001',
        verbose_name='Código Establecimiento',
        help_text='3 dígitos del establecimiento (ej: 001)'
    )
    punto_emision_codigo = models.CharField(
        max_length=3,
        default='001',
        verbose_name='Código Punto Emisión',
        help_text='3 dígitos del punto de emisión (ej: 001)'
    )
    secuencial = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Número Secuencial',
        help_text='Secuencial único de esta factura'
    )
    numero_factura = models.CharField(
        max_length=17,
        null=True,
        blank=True,
        verbose_name='Número de Factura',
        help_text='Formato: 001-001-000000001'
    )
    clave_acceso = models.CharField(
        max_length=49,
        blank=True,
        null=True,
        verbose_name='Clave de Acceso SRI',
        help_text='Clave de 49 dígitos generada según SRI'
    )
    fecha_autorizacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Autorización SRI'
    )
    estado_sri = models.CharField(
        max_length=20,
        choices=ESTADO_SRI_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado SRI'
    )
    
    def __str__(self):
        if self.numero_factura:
            return f"Factura {self.numero_factura} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        return f"Venta #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_totales(self):
        """
        Calcula automáticamente todos los totales de la venta.
        Debe llamarse después de agregar/modificar detalles.
        """
        from decimal import Decimal
        
        # Calcular subtotal de productos
        self.subtotal = sum(detalle.subtotal for detalle in self.detalleventa_set.all()) or Decimal('0')
        
        # Aplicar descuentos y recargos del cliente
        if self.cliente and hasattr(self.cliente, 'tasa_descuento') and hasattr(self.cliente, 'tasa_recargo'):
            if self.cliente.tasa_descuento > 0:
                descuento_cliente = self.subtotal * (self.cliente.tasa_descuento / 100)
                self.descuento_total += descuento_cliente
            
            if self.cliente.tasa_recargo > 0:
                recargo_cliente = self.subtotal * (self.cliente.tasa_recargo / 100)
                self.recargo_total += recargo_cliente
        
        # Calcular subtotal con descuentos y recargos
        subtotal_ajustado = self.subtotal - self.descuento_total + self.recargo_total
        
        # Calcular IVA (15% en Ecuador)
        self.iva = subtotal_ajustado * Decimal('0.15')
        
        # Calcular total final
        self.total = subtotal_ajustado + self.iva
        
        # Actualizar estado de pago según método
        if self.metodo_pago == 'credit':
            self.estado_pago = 'pendiente'
            self.saldo_pendiente = self.total
        else:
            self.estado_pago = 'pagado'
            self.saldo_pendiente = Decimal('0')
        
        self.save()
    
    def puede_pagar_credito(self):
        """
        Verifica si esta venta puede ser pagada a crédito.
        Consumidor Final NO puede comprar a crédito.
        """
        if not self.cliente:
            return False
        
        # 🎯 Consumidor Final NO puede comprar a crédito
        if hasattr(self.cliente, 'es_consumidor_final') and self.cliente.es_consumidor_final():
            return False
        
        if hasattr(self.cliente, 'puede_comprar_a_credito'):
            return self.cliente.puede_comprar_a_credito(self.total)
        return False
    
    def aplicar_pago(self, monto, metodo_pago='cash', referencia=None):
        """
        Aplica un pago a esta venta (útil para pagos de crédito).
        """
        from decimal import Decimal
        from apps.transacciones.models import Transaccion
        
        monto = Decimal(str(monto))
        
        # Validar que no se pague más de lo que se debe
        if monto > self.saldo_pendiente:
            raise ValueError(f"El monto ${monto} excede la deuda pendiente ${self.saldo_pendiente}")
        
        # Crear transacción de pago con snapshot del total
        transaccion = Transaccion.objects.create(
            venta=self,
            cliente=self.cliente,
            tipo_transaccion='pago_credito',
            metodo_pago=metodo_pago,
            monto=monto,
            venta_total_snapshot=self.total,  # Guardar snapshot
            referencia=referencia,
            usuario_creador=self.usuario_creador
        )
        
        # Actualizar saldo
        self.saldo_pendiente -= monto
        
        # Actualizar estado
        if self.saldo_pendiente == 0:
            self.estado_pago = 'pagado'
        elif self.saldo_pendiente < self.total:
            self.estado_pago = 'parcial'
        
        self.save()
        return transaccion
    
    def get_estado_pago_display_color(self):
        """
        Retorna el color CSS para mostrar el estado de pago.
        """
        colors = {
            'pagado': 'text-green-600',
            'parcial': 'text-yellow-600',
            'pendiente': 'text-red-600'
        }
        return colors.get(self.estado_pago, 'text-gray-600')
    
    @property
    def es_credito(self):
        """Verifica si esta venta es a crédito"""
        return self.metodo_pago == 'credit' or self.saldo_pendiente > 0
    
    def save(self, *args, **kwargs):
        """
        Override save para validar reglas de negocio de Consumidor Final.
        """
        # 🎯 VALIDACIÓN: Consumidor Final no puede tener descuentos ni recargos
        if self.cliente and hasattr(self.cliente, 'es_consumidor_final'):
            if self.cliente.es_consumidor_final():
                self.descuento_total = Decimal('0.00')
                self.recargo_total = Decimal('0.00')
                
                # Consumidor Final no puede comprar a crédito
                if self.metodo_pago == 'credit':
                    raise ValueError('Consumidor Final no puede comprar a crédito')
                
                # Consumidor Final siempre paga completo
                self.estado_pago = 'pagado'
                self.saldo_pendiente = Decimal('0.00')
        
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'ventas'
        constraints = [
            # 🎯 Unique constraint multi-tenant: cada usuario tiene su propia numeración
            models.UniqueConstraint(
                fields=['usuario_creador', 'numero_factura'],
                name='unique_numero_factura_por_usuario',
                condition=models.Q(numero_factura__isnull=False)
            )
        ]


class DetalleVenta(models.Model):
    """
    Model to store sale item details.
    Guarda una fotografía completa del producto en el momento de la venta.
    """
    # === RELACIONES ===
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalleventa_set')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True)  # PROTECT para no eliminar productos con ventas
    
    # Datos históricos del producto (fotografía del momento)
    nombre_producto = models.CharField(max_length=200)
    codigo_producto = models.CharField(max_length=50, null=True, blank=True)
    
    # === CANTIDADES ===
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0'))
    
    # === DESCUENTOS ===
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Descuento %")
    descuento_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento $")
    
    # === TOTALES ===
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    # === IMPUESTOS ===
    aplica_iva = models.BooleanField(default=True, verbose_name="Aplica IVA")
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'), verbose_name="% IVA")
    iva_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto IVA")
    
    # === METADATA ===
    notas = models.TextField(null=True, blank=True, verbose_name="Notas Especiales")
   
    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto}"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el subtotal y el IVA al guardar"""
        # Calcular descuento en monto si se especificó porcentaje
        if self.descuento_porcentaje > 0 and self.descuento_monto == 0:
            self.descuento_monto = (self.precio_unitario * self.descuento_porcentaje / 100)
        
        # Calcular subtotal
        precio_con_descuento = self.precio_unitario - self.descuento_monto
        self.subtotal = precio_con_descuento * self.cantidad
        
        # Calcular IVA si aplica
        if self.aplica_iva:
            self.iva_monto = self.subtotal * (self.iva_porcentaje / 100)
        else:
            self.iva_monto = Decimal('0')
        
        super().save(*args, **kwargs)
    
    @property
    def utilidad_linea(self):
        """Calcula la utilidad de esta línea basada en el costo del momento"""
        if self.costo_unitario:
            precio_base = self.precio_unitario / (Decimal('1') + self.iva_porcentaje / Decimal('100'))
            return (precio_base - self.costo_unitario) * Decimal(str(self.cantidad))
        return Decimal('0')
    
    @property
    def margen_porcentaje(self):
        """Calcula el margen porcentual de esta línea"""
        if self.costo_unitario and self.costo_unitario > 0:
            precio_base = self.precio_unitario / (Decimal('1') + self.iva_porcentaje / Decimal('100'))
            return ((precio_base - self.costo_unitario) / self.costo_unitario) * Decimal('100')
        return Decimal('0')
    
    class Meta:
        app_label = 'ventas'


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



class CajaSesion(models.Model):
    """
    Modelo para sesiones de caja (turnos de cajero).
    Permite control de arqueo de caja y auditoría.
    """
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
        ('auditada', 'Auditada'),
    ]
    
    # === IDENTIFICACIÓN ===
    business = models.ForeignKey(
        'usuarios.Business',
        on_delete=models.CASCADE,
        related_name='caja_sesiones',
        verbose_name='Negocio'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='caja_sesiones',
        verbose_name='Cajero'
    )
    punto_emision = models.ForeignKey(
        'PuntoEmision',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='caja_sesiones',
        verbose_name='Punto de Emisión'
    )
    
    # === FECHAS ===
    fecha_apertura = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Apertura')
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Cierre')
    
    # === MONTOS ===
    monto_inicial = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Monto Inicial',
        help_text='Efectivo con el que se abre la caja'
    )
    monto_esperado = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        verbose_name='Monto Esperado',
        help_text='Calculado: inicial + ventas cash - retiros'
    )
    monto_real = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Monto Real',
        help_text='Efectivo contado al cerrar'
    )
    diferencia = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        verbose_name='Diferencia',
        help_text='Real - Esperado (positivo = sobrante, negativo = faltante)'
    )
    
    # === ESTADO ===
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='abierta',
        verbose_name='Estado'
    )
    
    # === NOTAS ===
    notas_apertura = models.TextField(null=True, blank=True, verbose_name='Notas de Apertura')
    notas_cierre = models.TextField(null=True, blank=True, verbose_name='Notas de Cierre')
    
    class Meta:
        verbose_name = 'Sesión de Caja'
        verbose_name_plural = 'Sesiones de Caja'
        ordering = ['-fecha_apertura']
        indexes = [
            models.Index(fields=['business', 'usuario', 'estado']),
            models.Index(fields=['fecha_apertura']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"Caja {self.usuario.username} - {self.fecha_apertura.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_monto_esperado(self):
        """
        Calcula el monto esperado basado en:
        - Monto inicial
        - Ventas en efectivo
        - Retiros (si se implementan)
        """
        from decimal import Decimal
        
        # Obtener ventas en efectivo de esta sesión
        ventas_cash = Venta.objects.filter(
            usuario_creador=self.usuario,
            fecha_hora__gte=self.fecha_apertura,
            metodo_pago='cash'
        )
        
        if self.fecha_cierre:
            ventas_cash = ventas_cash.filter(fecha_hora__lte=self.fecha_cierre)
        
        total_ventas_cash = sum(v.total for v in ventas_cash) or Decimal('0')
        
        self.monto_esperado = self.monto_inicial + total_ventas_cash
        return self.monto_esperado
    
    def cerrar_caja(self, monto_real, notas_cierre=None):
        """
        Cierra la sesión de caja y calcula diferencias.
        """
        from django.utils import timezone
        from decimal import Decimal
        
        self.fecha_cierre = timezone.now()
        self.monto_real = Decimal(str(monto_real))
        self.notas_cierre = notas_cierre
        
        # Calcular monto esperado
        self.calcular_monto_esperado()
        
        # Calcular diferencia
        self.diferencia = self.monto_real - self.monto_esperado
        
        # Cambiar estado
        self.estado = 'cerrada'
        
        self.save()
        
        return {
            'monto_esperado': float(self.monto_esperado),
            'monto_real': float(self.monto_real),
            'diferencia': float(self.diferencia),
            'estado': 'sobrante' if self.diferencia > 0 else 'faltante' if self.diferencia < 0 else 'exacto'
        }
    
    @classmethod
    def get_sesion_activa(cls, usuario):
        """
        Obtiene la sesión activa del usuario o None.
        """
        return cls.objects.filter(
            usuario=usuario,
            estado='abierta'
        ).first()
    
    @classmethod
    def abrir_nueva_sesion(cls, usuario, business, monto_inicial, punto_emision=None, notas=None):
        """
        Abre una nueva sesión de caja.
        Valida que no haya otra sesión abierta.
        """
        # Verificar que no haya sesión abierta
        sesion_activa = cls.get_sesion_activa(usuario)
        if sesion_activa:
            raise ValueError(f'Ya existe una sesión abierta desde {sesion_activa.fecha_apertura}')
        
        # Crear nueva sesión
        sesion = cls.objects.create(
            business=business,
            usuario=usuario,
            punto_emision=punto_emision,
            monto_inicial=monto_inicial,
            notas_apertura=notas
        )
        
        return sesion
