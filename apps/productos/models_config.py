"""
Configuración de visualización de productos adaptable por contexto
"""
from django.db import models
from django.conf import settings


class ProductDisplayConfig(models.Model):
    """
    Configuración personalizada de cómo se muestran los productos
    Permite experiencias adaptadas sin estar amarrado solo al modo_operacion
    """
    
    VISTA_CHOICES = [
        ('grid', 'Vista Grid (Tarjetas)'),
        ('list', 'Vista Lista (Compacta)'),
        ('table', 'Vista Tabla (Detallada)'),
    ]
    
    ORDEN_CHOICES = [
        ('nombre', 'Nombre A-Z'),
        ('-nombre', 'Nombre Z-A'),
        ('precio', 'Precio: Menor a Mayor'),
        ('-precio', 'Precio: Mayor a Menor'),
        ('stock', 'Stock: Menor a Mayor'),
        ('-stock', 'Stock: Mayor a Menor'),
        ('-fecha_creacion', 'Más Recientes'),
        ('fecha_creacion', 'Más Antiguos'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_display_config'
    )
    
    # Vista predeterminada
    vista_predeterminada = models.CharField(
        max_length=10,
        choices=VISTA_CHOICES,
        default='grid',
        verbose_name='Vista Predeterminada'
    )
    
    # Orden predeterminado
    orden_predeterminado = models.CharField(
        max_length=20,
        choices=ORDEN_CHOICES,
        default='-fecha_creacion',
        verbose_name='Orden Predeterminado'
    )
    
    # Opciones de visualización
    mostrar_imagenes = models.BooleanField(
        default=True,
        verbose_name='Mostrar Imágenes'
    )
    
    mostrar_codigo_barras = models.BooleanField(
        default=True,
        verbose_name='Mostrar Código de Barras'
    )
    
    mostrar_stock = models.BooleanField(
        default=True,
        verbose_name='Mostrar Stock'
    )
    
    mostrar_categoria = models.BooleanField(
        default=True,
        verbose_name='Mostrar Categoría'
    )
    
    mostrar_descripcion = models.BooleanField(
        default=False,
        verbose_name='Mostrar Descripción'
    )
    
    # Tamaño de imágenes en grid
    tamano_imagen_grid = models.CharField(
        max_length=10,
        choices=[
            ('small', 'Pequeño'),
            ('medium', 'Mediano'),
            ('large', 'Grande'),
        ],
        default='medium',
        verbose_name='Tamaño de Imagen en Grid'
    )
    
    # Filtros activos
    filtros_avanzados_activos = models.BooleanField(
        default=True,
        verbose_name='Activar Filtros Avanzados'
    )
    
    busqueda_codigo_barras_prioritaria = models.BooleanField(
        default=False,
        verbose_name='Priorizar Búsqueda por Código de Barras'
    )
    
    # Alertas visuales
    alerta_stock_bajo = models.BooleanField(
        default=True,
        verbose_name='Mostrar Alerta de Stock Bajo'
    )
    
    umbral_stock_bajo = models.PositiveIntegerField(
        default=10,
        verbose_name='Umbral de Stock Bajo'
    )
    
    # Productos por página
    productos_por_pagina = models.PositiveIntegerField(
        default=20,
        verbose_name='Productos por Página'
    )
    
    # Auto-configuración basada en modo
    auto_configurar_por_modo = models.BooleanField(
        default=True,
        verbose_name='Auto-configurar según Modo de Operación'
    )
    
    class Meta:
        verbose_name = 'Configuración de Vista de Productos'
        verbose_name_plural = 'Configuraciones de Vista de Productos'
    
    def __str__(self):
        return f"Config de {self.user.username}"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Obtiene o crea la configuración para un usuario
        Si auto_configurar_por_modo está activo, ajusta según el modo del negocio SOLO al crear
        """
        config, created = cls.objects.get_or_create(user=user)
        
        # SOLO aplicar preset automático si se acaba de crear
        if created:
            # Intentar obtener el modo de operación del negocio
            try:
                from apps.usuarios.models import Business
                business = Business.objects.get(user=user)
                modo = business.modo_operacion
                
                if modo == 'restaurante':
                    config.aplicar_preset_restaurante()
                elif modo == 'retail':
                    config.aplicar_preset_retail()
                    
            except:
                pass
        
        return config
    
    def aplicar_preset_restaurante(self):
        """Configuración optimizada para restaurantes"""
        self.vista_predeterminada = 'grid'
        self.orden_predeterminado = '-fecha_creacion'
        self.mostrar_imagenes = True
        self.mostrar_codigo_barras = False
        self.mostrar_stock = False
        self.mostrar_categoria = True
        self.mostrar_descripcion = True
        self.tamano_imagen_grid = 'large'
        self.filtros_avanzados_activos = False
        self.busqueda_codigo_barras_prioritaria = False
        self.alerta_stock_bajo = False
        self.productos_por_pagina = 12
        self.save()
    
    def aplicar_preset_retail(self):
        """Configuración optimizada para retail"""
        self.vista_predeterminada = 'list'
        self.orden_predeterminado = 'nombre'
        self.mostrar_imagenes = False
        self.mostrar_codigo_barras = True
        self.mostrar_stock = True
        self.mostrar_categoria = True
        self.mostrar_descripcion = False
        self.tamano_imagen_grid = 'small'
        self.filtros_avanzados_activos = True
        self.busqueda_codigo_barras_prioritaria = True
        self.alerta_stock_bajo = True
        self.productos_por_pagina = 50
        self.save()


class SavedProductFilter(models.Model):
    """
    Filtros guardados por el usuario para acceso rápido
    Permite crear vistas personalizadas tipo "Administrador", "Cajero", "Inventario"
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_product_filters'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Filtro'
    )
    
    # Descripción opcional
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción'
    )
    
    # Filtros guardados como JSON
    filtros = models.JSONField(
        default=dict,
        verbose_name='Filtros',
        help_text='Incluye: categoria, stock_bajo, sin_imagen, orden, vista, etc.'
    )
    
    # Configuración de visualización específica para esta vista
    config_vista = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuración de Vista',
        help_text='Configuración específica de visualización para esta vista guardada'
    )
    
    es_favorito = models.BooleanField(
        default=False,
        verbose_name='Filtro Favorito'
    )
    
    # Icono para identificar visualmente
    icono = models.CharField(
        max_length=50,
        default='filter',
        verbose_name='Icono',
        help_text='Nombre del icono de lucide'
    )
    
    # Color para el chip
    color = models.CharField(
        max_length=20,
        default='emerald',
        choices=[
            ('emerald', 'Verde'),
            ('blue', 'Azul'),
            ('purple', 'Morado'),
            ('orange', 'Naranja'),
            ('red', 'Rojo'),
            ('yellow', 'Amarillo'),
        ],
        verbose_name='Color'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True
    )
    
    # Contador de uso
    veces_usado = models.PositiveIntegerField(
        default=0,
        verbose_name='Veces Usado'
    )
    
    class Meta:
        verbose_name = 'Filtro Guardado'
        verbose_name_plural = 'Filtros Guardados'
        ordering = ['-es_favorito', '-veces_usado', '-fecha_modificacion']
        unique_together = ['user', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.user.username})"
    
    def incrementar_uso(self):
        """Incrementa el contador de uso"""
        self.veces_usado += 1
        self.save(update_fields=['veces_usado'])
