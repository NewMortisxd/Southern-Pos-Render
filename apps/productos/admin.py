from django.contrib import admin
from .models import Producto, Categoria
from .models_config import ProductDisplayConfig, SavedProductFilter


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'categoria', 'codigo_barras', 'usuario_creador']
    list_filter = ['categoria', 'usuario_creador']
    search_fields = ['nombre', 'codigo_barras', 'descripcion']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario_creador']
    search_fields = ['nombre']


@admin.register(ProductDisplayConfig)
class ProductDisplayConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'vista_predeterminada', 'orden_predeterminado', 'auto_configurar_por_modo']
    list_filter = ['vista_predeterminada', 'auto_configurar_por_modo']


@admin.register(SavedProductFilter)
class SavedProductFilterAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'user', 'es_favorito', 'fecha_creacion']
    list_filter = ['es_favorito', 'user']
