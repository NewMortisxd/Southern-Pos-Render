from django.urls import path
from . import views

# Define el espacio de nombres para la aplicación
app_name = 'productos'

# Patrones de URL para las vistas de la aplicación
urlpatterns = [
    # Ruta para la lista de productos
    path('', views.lista_productos, name='lista'),
    # Ruta para crear un nuevo producto
    path('nuevo/', views.crear_producto, name='crear'),
    # Ruta para editar un producto existente, usando el ID (pk)
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    # Ruta para eliminar un producto, usando el ID (pk)
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
    # Rutas para gestión de categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='categoria_create'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    # Ruta para buscar productos
    path('buscar/', views.buscar_productos, name='buscar'),
    path('api/buscar-por-codigo/', views.buscar_producto_por_codigo, name='buscar_por_codigo'),
    # Rutas para configuración de visualización
    path('configuracion/', views.config_productos, name='configuracion'),
    path('api/actualizar-config/', views.actualizar_config_vista, name='actualizar_config'),
    path('api/guardar-filtro/', views.guardar_filtro, name='guardar_filtro'),
    path('vistas/', views.gestionar_vistas, name='gestionar_vistas'),
    path('filtro/<int:filtro_id>/aplicar/', views.aplicar_filtro_guardado, name='aplicar_filtro'),
    path('filtro/<int:filtro_id>/editar/', views.editar_filtro_guardado, name='editar_filtro'),
    path('filtro/<int:filtro_id>/eliminar/', views.eliminar_filtro_guardado, name='eliminar_filtro'),
    path('filtro/<int:filtro_id>/favorito/', views.toggle_favorito_filtro, name='toggle_favorito'),
    path('preset/<str:preset>/', views.aplicar_preset, name='aplicar_preset'),
]