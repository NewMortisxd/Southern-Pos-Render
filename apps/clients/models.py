from django.db import models
from django.conf import settings

# Modelo para los clientes
class Cliente(models.Model):
    # Relación con el usuario creador
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clientes',
        null=True
    )
    
    # Opciones para el campo grupo
    GRUPO_CHOICES = [
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('corporativo', 'Corporativo'),
    ]
    
    # Opciones para el campo estado
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]
    
    # Opciones para el campo crédito
    CREDITO_CHOICES = [
        (0, 'Sin crédito'),
        (15, '15 días'),
        (30, '30 días'),
        (45, '45 días'),
        (60, '60 días'),
        (90, '90 días'),
    ]
    
    # Campos del modelo
    codigo = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    razon_social = models.CharField(max_length=200, blank=True, null=True, verbose_name="Razón Social")
    identificacion = models.CharField(max_length=20, verbose_name="Identificación")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    grupo = models.CharField(max_length=20, choices=GRUPO_CHOICES, default='regular', verbose_name="Grupo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    # Nuevos campos
    credito = models.IntegerField(choices=CREDITO_CHOICES, default=0, verbose_name="Crédito (días)")
    cupo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cupo")
    tasa_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tasa de descuento (%)")
    tasa_recargo = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tasa de recargo (%)")
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
    
    # Representación en cadena del objeto
    def __str__(self):
        return self.nombre