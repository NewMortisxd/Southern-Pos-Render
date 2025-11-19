from django.urls import path
from . import views

# Define el espacio de nombres para la aplicación
app_name = 'clients'

# Patrones de URL para las vistas de la aplicación
urlpatterns = [
    # Ruta para la lista de clientes
    path('', views.lista_clientes, name='lista'),
    # Ruta para agregar un nuevo cliente
    path('agregar/', views.agregar_cliente, name='agregar'),
    # Ruta para editar un cliente existente, usando el ID (cliente_id)
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar'),
    # Ruta para eliminar un cliente, usando el ID (cliente_id)
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar'),
    # Ruta para ver los detalles de un cliente, usando el ID (cliente_id)
    path('detalle/<int:cliente_id>/', views.detalle_cliente, name='detalle'),
    # Ruta para la búsqueda de clientes
    path('search/', views.client_search_view, name='client_search'),
]