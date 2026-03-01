from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

class Usuario(AbstractUser):
    nombre_completo = models.CharField(max_length=150, blank=False)
    email = models.EmailField(unique=True)
    
    # Campos de información del negocio
    direccion_negocio = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección del negocio/local")
    telefono_negocio = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono del negocio/local")
    ruc_negocio = models.CharField(max_length=20, blank=True, null=True, verbose_name="RUC negocio/local")
    email_negocio = models.EmailField(blank=True, null=True, verbose_name="Email negocio/local")
    
    # Campos con related_name únicos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_groups',
        related_query_name='custom_user_group'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre_completo']
    
    def __str__(self):
        return self.email


# Asumiendo que tienes un modelo de perfil o negocio, agrega el campo nombre_negocio
# Por ejemplo, si tienes un modelo Business o Profile:

# Update your Business model
class Business(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('restaurant', 'Restaurante'),
        ('retail', 'Retail/Supermercado'),
        ('hybrid', 'Híbrido'),
    ]
    
    MODO_OPERACION_CHOICES = [
        ('restaurante', 'Modo Restaurante'),
        ('retail', 'Modo Retail/Supermercado'),
    ]
    
    PLAN_CHOICES = [
        ('free', 'Plan Gratuito'),
        ('pro', 'Plan Pro'),
        ('enterprise', 'Plan Enterprise'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre_negocio = models.CharField(max_length=255, blank=True, null=True)
    direccion_negocio = models.CharField(max_length=255, blank=True, null=True)
    telefono_negocio = models.CharField(max_length=20, blank=True, null=True)
    ruc_negocio = models.CharField(max_length=20, blank=True, null=True)
    email_negocio = models.EmailField(blank=True, null=True)
    
    # Plan de suscripción
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='free',
        verbose_name="Plan de Suscripción"
    )
    
    # Tax settings
    iva_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.00,  # Tarifa vigente desde abril 2024
        verbose_name="Porcentaje de IVA",
        help_text="Tarifa vigente: 15%. Históricas: 0%, 12%, 14%"
    )
    
    # Receipt settings
    mostrar_logo_en_factura = models.BooleanField(default=True, verbose_name="Mostrar Logo en Factura")
    mensaje_factura = models.TextField(blank=True, null=True, verbose_name="Mensaje en Factura", 
                                      default="¡Gracias por su compra!")
    politica_devolucion = models.TextField(blank=True, null=True, verbose_name="Política de Devolución",
                                         default="Para devoluciones, presente este comprobante dentro de los próximos 7 días.")
    
    # System settings
    moneda = models.CharField(max_length=10, default="$", verbose_name="Símbolo de Moneda")
    formato_fecha = models.CharField(max_length=20, default="d/m/Y", verbose_name="Formato de Fecha")
    
    # Personalization fields
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True, verbose_name="Logo de Personalización")
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name="Logo de Empresa")
    use_custom_logo = models.BooleanField(default=False)
    primary_color = models.CharField(max_length=7, default='#10b981')
    secondary_color = models.CharField(max_length=7, default='#6366f1')
    default_view = models.CharField(max_length=10, default='grid')
    show_product_images = models.BooleanField(default=True)
    use_custom_brand_name = models.BooleanField(default=False)
    custom_brand_name = models.CharField(max_length=12, blank=True)
    dark_mode = models.BooleanField(default=False)
    
    # Modo de operación (mantener compatibilidad)
    modo_operacion = models.CharField(
        max_length=20,
        choices=MODO_OPERACION_CHOICES,
        default='restaurante'
    )
    
    # Nuevos campos para modo restaurante
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPE_CHOICES,
        default='restaurant',
        verbose_name="Tipo de Negocio"
    )
    
    # Configuración de pantallas para restaurante
    enable_orders = models.BooleanField(
        default=False,
        verbose_name="Habilitar Sistema de Órdenes"
    )
    enable_kds = models.BooleanField(
        default=False,
        verbose_name="Mostrar Pantalla de Cocina en Sidebar"
    )
    enable_public_display = models.BooleanField(
        default=False,
        verbose_name="Mostrar Pantalla Pública en Sidebar"
    )
    
    # Contador de órdenes (para generación secuencial)
    last_order_number = models.PositiveIntegerField(
        default=0,
        verbose_name="Último Número de Orden"
    )
    
    # Campos de Facturación Electrónica SRI (Opcionales)
    razon_social_legal = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Razón Social Legal",
        help_text="Exactamente como aparece en el RUC"
    )
    ambiente_sri = models.CharField(
        max_length=1,
        choices=[('1', 'Pruebas'), ('2', 'Producción')],
        default='1',
        verbose_name="Ambiente SRI"
    )
    tipo_emision = models.CharField(
        max_length=1,
        choices=[('1', 'Emisión Normal'), ('2', 'Emisión por Indisponibilidad')],
        default='1',
        verbose_name="Tipo de Emisión"
    )
    obligado_contabilidad = models.CharField(
        max_length=2,
        choices=[('SI', 'SI'), ('NO', 'NO')],
        default='NO',
        verbose_name="Obligado a llevar contabilidad"
    )
    regimen_rimpe = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('', 'No aplica'),
            ('RIMPE', 'RIMPE'),
            ('RIMPE_EMPRENDEDOR', 'RIMPE - Emprendedor'),
            ('NO', 'NO')
        ],
        verbose_name="Régimen RIMPE"
    )
    establecimiento = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="Establecimiento",
        help_text="3 dígitos (ej: 001)"
    )
    punto_emision = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="Punto de Emisión",
        help_text="3 dígitos (ej: 001)"
    )
    
    def __str__(self):
        return self.nombre_negocio or self.user.username
    
    def supports_orders(self):
        """Verifica si el negocio soporta pedidos (sistema de órdenes habilitado)"""
        return self.enable_orders