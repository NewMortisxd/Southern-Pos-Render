from django.db import models
from django.conf import settings

class BusinessConfiguration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_config')
    nombre_negocio = models.CharField(max_length=100, verbose_name="Nombre del Negocio")
    direccion_negocio = models.TextField(verbose_name="Dirección", blank=True, null=True)
    ciudad_negocio = models.CharField(max_length=50, verbose_name="Ciudad", blank=True, null=True)
    telefono_negocio = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    email_negocio = models.EmailField(verbose_name="Email", blank=True, null=True)
    ruc_negocio = models.CharField(max_length=20, verbose_name="RUC/NIT", blank=True, null=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True, verbose_name="Logo")
    
    # Tax settings
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, verbose_name="Porcentaje de IVA")
    
    # Receipt settings
    mostrar_logo_en_factura = models.BooleanField(default=True, verbose_name="Mostrar Logo en Factura")
    mensaje_factura = models.TextField(blank=True, null=True, verbose_name="Mensaje en Factura", 
                                      default="¡Gracias por su compra!")
    politica_devolucion = models.TextField(blank=True, null=True, verbose_name="Política de Devolución",
                                         default="Para devoluciones, presente este comprobante dentro de los próximos 7 días.")
    
    # System settings
    moneda = models.CharField(max_length=10, default="$", verbose_name="Símbolo de Moneda")
    formato_fecha = models.CharField(max_length=20, default="d/m/Y", verbose_name="Formato de Fecha")
    
    def __str__(self):
        return f"Configuración de {self.nombre_negocio}"
    
    class Meta:
        verbose_name = "Configuración de Negocio"
        verbose_name_plural = "Configuraciones de Negocio"

