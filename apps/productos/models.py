from django.db import models
from django.conf import settings
import os
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

# Importar modelos de configuración
from .models_config import ProductDisplayConfig, SavedProductFilter

def producto_imagen_path(instance, filename):
    """
    Genera una ruta de archivo personalizada para las imágenes de productos,
    truncando el nombre si es demasiado largo
    """
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    # Obtener el nombre base sin extensión
    base_name = os.path.splitext(filename)[0]
    
    # Slugify y truncar el nombre a 50 caracteres para dejar espacio para la ruta
    safe_name = slugify(base_name)[:50]
    
    # Construir el nombre final
    new_filename = f"{safe_name}.{ext}"
    
    # Retornar la ruta completa
    return os.path.join('productos', new_filename)

# Modelo para la categoría de productos
class Categoria(models.Model):
    # Nombre de la categoría, máximo 100 caracteres
    nombre = models.CharField(max_length=100)
    # Descripción de la categoría, opcional
    descripcion = models.TextField(blank=True)
    # Relación con el usuario que creó la categoría
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='categorias', 
        null=True
    )
    
    # Representación en cadena del objeto
    def __str__(self):
        return self.nombre

    class Meta:
        # Nombre singular para la interfaz de administración
        verbose_name = "Categoría"
        # Nombre plural para la interfaz de administración
        verbose_name_plural = "Categorías"

# Modelo para los productos
class Producto(models.Model):
    TIPO_PRODUCTO_CHOICES = [
        ('fisico', 'Producto físico'),
        ('servicio', 'Servicio'),
        ('combo', 'Combo / Plato'),
        ('insumo', 'Insumo / Materia prima'),
    ]
    
    UNIDAD_MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('porcion', 'Porción'),
        ('kg', 'Kilogramo'),
        ('g', 'Gramo'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('caja', 'Caja'),
        ('paquete', 'Paquete'),
        ('docena', 'Docena'),
    ]
    
    # Nombre del producto, máximo 100 caracteres
    nombre = models.CharField(max_length=100)
    
    # Tipo de producto (obligatorio)
    tipo_producto = models.CharField(
        max_length=20, 
        choices=TIPO_PRODUCTO_CHOICES, 
        default='fisico',
        verbose_name="Tipo de producto"
    )
    
    # SKU / Código interno (generado automáticamente si no se proporciona)
    sku = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="SKU / Código interno"
    )
    
    # Precio base (sin IVA)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio base", default=0)
    # Costo del producto (para cálculo de inventario real)
    costo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo", default=0, null=True, blank=True)
    # Si el precio ingresado incluye IVA
    incluye_iva = models.BooleanField(default=True, verbose_name="Precio incluye IVA")
    # Descripción detallada del producto
    descripcion = models.TextField(blank=True)  # Hacerlo opcional
    
    # Control de inventario
    controla_stock = models.BooleanField(default=True, verbose_name="Controlar stock")
    # Cantidad en stock, solo valores enteros positivos (null si no controla stock)
    stock = models.PositiveIntegerField(null=True, blank=True, default=0)
    # Stock mínimo para alertas
    stock_minimo = models.PositiveIntegerField(null=True, blank=True, default=5, verbose_name="Stock mínimo")
    # Unidad de medida
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_MEDIDA_CHOICES,
        default='unidad',
        verbose_name="Unidad de medida"
    )
    # Imagen del producto, se guarda en Cloudinary
    imagen = CloudinaryField('imagen', folder='productos', blank=True, null=True)  # Cloudinary field
    # Código de barras del producto, opcional
    codigo_barras = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Código de barras"
    )  # Añadido campo de código de barras
    # Relación con la categoría, permite valor nulo
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    # Fecha de creación del producto, se establece automáticamente
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Relación con el usuario que creó el producto
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='productos', 
        null=True
    )
    
    # Soft delete - No eliminar físicamente productos con historial
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    # Auditoría y trazabilidad (ERP level)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")

    # Representación en cadena del objeto
    def __str__(self):
        return self.nombre
    
    def generar_sku(self):
        """Genera un SKU único automáticamente"""
        # Prefijo basado en categoría
        if self.categoria:
            prefijo = ''.join(c for c in self.categoria.nombre if c.isalnum())[:3].upper()
        else:
            prefijo = 'PRD'
        
        # Buscar el último SKU con este prefijo
        ultimo_sku = Producto.objects.filter(
            sku__startswith=prefijo
        ).order_by('-id').first()
        
        if ultimo_sku and ultimo_sku.sku:
            try:
                # Extraer el número del último SKU
                partes = ultimo_sku.sku.split('-')
                if len(partes) >= 2:
                    ultimo_numero = int(partes[-1])
                    nuevo_numero = ultimo_numero + 1
                else:
                    nuevo_numero = 1
            except (ValueError, IndexError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        return f"{prefijo}-{nuevo_numero:04d}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para generar SKU automáticamente si no existe"""
        if not self.sku:
            self.sku = self.generar_sku()
        super().save(*args, **kwargs)
    
    def get_iva_porcentaje(self):
        """Obtiene el porcentaje de IVA de la configuración del negocio"""
        from decimal import Decimal
        try:
            from apps.usuarios.models import Business
            business = Business.objects.filter(user=self.usuario_creador).first()
            if business and business.iva_porcentaje:
                return business.iva_porcentaje
        except:
            pass
        return Decimal('15')  # Default 15% para Ecuador
    
    @property
    def precio(self):
        """Precio final con IVA incluido (para compatibilidad con código existente)"""
        from decimal import Decimal, ROUND_HALF_UP
        iva_porcentaje = self.get_iva_porcentaje()
        precio_calculado = self.precio_base * (Decimal('1') + iva_porcentaje / Decimal('100'))
        # Redondear a 2 decimales
        return precio_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def precio_sin_iva(self):
        """Precio base sin IVA"""
        return self.precio_base
    
    @property
    def monto_iva(self):
        """Monto del IVA"""
        return self.precio - self.precio_base
    
    @property
    def valor_inventario_costo(self):
        """Valor del inventario basado en costo (contablemente correcto)"""
        from decimal import Decimal
        if self.controla_stock and self.stock and self.costo:
            return self.costo * Decimal(str(self.stock))
        return Decimal('0')
    
    @property
    def valor_inventario_venta(self):
        """Valor del inventario basado en precio de venta"""
        from decimal import Decimal
        if self.controla_stock and self.stock:
            return self.precio * Decimal(str(self.stock))
        return Decimal('0')
    
    @property
    def margen_utilidad(self):
        """Margen de utilidad del producto"""
        from decimal import Decimal
        if self.costo and self.costo > 0:
            return ((self.precio_base - self.costo) / self.costo) * Decimal('100')
        return Decimal('0')


# Exportar todos los modelos
__all__ = ['Producto', 'Categoria', 'ProductDisplayConfig', 'SavedProductFilter']
