# Sistema de Órdenes para Restaurantes - SouthernPOS

## Descripción General

El sistema de órdenes es una funcionalidad avanzada diseñada específicamente para negocios en **Modo Restaurante**. Permite gestionar pedidos en tiempo real mediante dos pantallas especializadas: Kitchen Display System (KDS) y Pantalla Pública de turnos.

---

## Características Principales

### 1. Configuración del Negocio

En la página de configuraciones del negocio (`Business`), cuando el modo está configurado como **Restaurante**, se habilitan dos opciones adicionales:

- **📺 Pantalla de Cocina (KDS - Kitchen Display System)**: Sistema para que la cocina visualice y gestione pedidos en tiempo real
- **📢 Pantalla Pública (Turnos)**: Pantalla para que los clientes vean cuándo su pedido está listo

Estas opciones se activan/desactivan mediante checkboxes en la configuración del negocio.

### 2. ID de Pedido Único

Cada venta en modo restaurante genera un **ID de pedido único** (Order Number) que:

- Es secuencial por negocio (1, 2, 3, ...)
- Se muestra en todas las interfaces relacionadas con el pedido
- Aparece en facturas y comprobantes de restaurante
- **NO se genera en modo supermercado** (el campo queda vacío)
- Es escalable y único por sistema POS

**Visibilidad del ID:**
- ✅ Visible en: KDS, Pantalla Pública, Facturas de Restaurante, Venta Completa, Transacciones
- ❌ Oculto en: Modo Supermercado (todas las vistas)

---

## Componentes del Sistema

### 1. Kitchen Display System (KDS)

**Ruta:** `/kds/kitchen/`

**Características:**
- Pantalla fullscreen sin dashboard
- Muestra logo del restaurante (si está configurado) o logo del sistema
- Muestra nombre del restaurante o "SouthernPOS" por defecto
- Actualización en tiempo real vía WebSocket
- Filtros por estado: Todos, En Proceso, Pendiente, En Cocina, Listos

**Estados de Pedidos:**
1. **PENDING (Pendiente)** - Color naranja
   - Pedido recién creado
   - Acciones: Iniciar preparación, Cancelar
   
2. **PREPARING (En Preparación)** - Color azul
   - Pedido en cocina
   - Acciones: Marcar como listo, Regresar a pendiente, Cancelar
   
3. **READY (Listo)** - Color verde
   - Pedido listo para recoger
   - Acciones: Marcar como entregado, Regresar a cocina
   
4. **DELIVERED (Entregado)** - Se oculta automáticamente
5. **CANCELLED (Cancelado)** - Se oculta automáticamente

**Información Mostrada:**
- Número de pedido (#1, #2, etc.)
- Estado actual con badge visual
- Tiempo transcurrido desde creación
- Lista de productos con cantidades
- Notas adicionales (si existen)

**Funcionalidades:**
- Modal de confirmación para cancelar pedidos
- Animaciones suaves al cambiar estados
- Contador de pedidos activos
- Actualización automática de tiempos
- Filtrado dinámico que se mantiene al actualizar estados
- Loader de pantalla completa durante actualizaciones

### 2. Pantalla Pública (Public Display)

**Ruta:** `/kds/display/`

**Características:**
- Pantalla fullscreen sin dashboard
- Diseño optimizado para visualización a distancia
- Actualización en tiempo real vía WebSocket
- Sonido de notificación cuando un pedido está listo
- Responsive (desktop y mobile)

**Layout Desktop:**
- **Columna Izquierda (33%)**: Pedidos en preparación (azul)
- **Columna Derecha (67%)**: Pedidos listos (verde) - PRINCIPAL

**Layout Mobile:**
- **Sección Superior (Principal)**: Pedidos listos en grid 2 columnas
- **Sección Inferior (Secundaria)**: Pedidos en preparación en scroll horizontal

**Información Mostrada:**
- Número de pedido grande y visible
- Estado "¡LISTO!" para pedidos listos
- Contador de pedidos por estado
- Iconos visuales (check para listos, flame para preparación)

**Características Visuales:**
- Grid adaptativo que se ajusta al número de pedidos
- Sin scrollbar hasta que sea necesario
- Tarjetas centradas cuando hay pocos pedidos (1-3)
- Tamaño máximo de tarjetas: 350px (desktop), 200px (mobile)
- Animaciones de entrada/salida suaves
- Efecto pulse en pedidos listos

### 3. Integración con Ventas

**Flujo de Creación de Pedido:**

1. Usuario completa una venta en `/ventas/completar/`
2. Sistema detecta que el negocio tiene modo restaurante habilitado
3. Se crea automáticamente un `Order` asociado a la venta
4. Se genera un número de pedido secuencial
5. El pedido aparece instantáneamente en KDS (estado PENDING)
6. WebSocket notifica a todas las pantallas conectadas

**Modelo Order:**
```python
class Order(models.Model):
    business = ForeignKey(Business)  # Multi-tenant
    order_number = PositiveIntegerField()  # Secuencial por negocio
    status = CharField(choices=STATUS_CHOICES)
    created_at = DateTimeField()
    preparing_at = DateTimeField(null=True)
    ready_at = DateTimeField(null=True)
    delivered_at = DateTimeField(null=True)
    cancelled_at = DateTimeField(null=True)
    notes = TextField(blank=True)
```

**Relación con Venta:**
```python
class Venta(models.Model):
    # ... campos existentes ...
    order = ForeignKey(Order, null=True, blank=True)
```

---

## Arquitectura Técnica

### Backend

**Vistas Principales:**
- `kds_view()`: Renderiza la pantalla KDS
- `kds_orders_json()`: API para obtener órdenes activas (AJAX)
- `kds_update_status()`: Actualiza estado de una orden
- `public_display_view()`: Renderiza la pantalla pública
- `display_orders_json()`: API para órdenes en pantalla pública

**Servicios:**
- `OrderService.get_active_orders()`: Obtiene órdenes PENDING, PREPARING, READY
- `OrderService.get_ready_orders()`: Obtiene solo órdenes READY
- `OrderService.update_order_status()`: Actualiza estado y timestamps
- `OrderService.create_order_number()`: Genera número secuencial
- `OrderService.create_order_for_sale()`: Crea orden para una venta

**Decoradores Personalizados:**
- `@ajax_login_required`: Verifica autenticación y devuelve JSON en lugar de redireccionar

**Validación de Transiciones:**
```python
allowed_transitions = {
    'PENDING': ['PREPARING', 'CANCELLED'],
    'PREPARING': ['READY', 'PENDING', 'CANCELLED'],
    'READY': ['DELIVERED', 'PREPARING'],
}
```

### Frontend

**Tecnologías:**
- Tailwind CSS para estilos
- Lucide Icons para iconografía
- WebSocket para actualizaciones en tiempo real
- Fetch API para peticiones AJAX

**Funciones JavaScript Clave (KDS):**
- `connectWebSocket()`: Establece conexión WebSocket
- `handleWebSocketMessage()`: Procesa mensajes del servidor
- `updateStatus()`: Actualiza estado de orden vía AJAX
- `addNewOrderCard()`: Agrega nueva orden dinámicamente
- `updateOrderCardDynamic()`: Actualiza orden existente
- `createOrderCardHTML()`: Genera HTML de tarjeta de orden
- `filterOrders()`: Filtra órdenes por estado
- `applyCurrentFilter()`: Reaplica filtro actual
- `showCancelModal()`: Muestra modal de confirmación
- `confirmCancel()`: Confirma cancelación de pedido

**Funciones JavaScript Clave (Public Display):**
- `loadOrders()`: Carga órdenes desde API
- `updateOrdersDisplay()`: Actualiza ambas pantallas
- `updatePreparingOrders()`: Actualiza sección de preparación
- `updateReadyOrders()`: Actualiza sección de listos
- `playSound()`: Reproduce sonido de notificación

**Características de UX:**
- Loader de pantalla completa durante actualizaciones
- Modal de confirmación para acciones destructivas
- Animaciones suaves (slideIn, slideOut, pulse)
- Actualización automática de tiempos transcurridos
- Manejo de errores con mensajes claros
- Detección de sesión expirada

---

## Flujo de Trabajo Completo

### Escenario: Pedido de Restaurante

1. **Cliente realiza pedido**
   - Cajero ingresa productos en `/ventas/completar/`
   - Sistema detecta modo restaurante
   - Se genera Order #15 automáticamente

2. **Pedido aparece en KDS**
   - Estado: PENDING (naranja)
   - Muestra: #15, productos, tiempo 0 min
   - Cocina ve el pedido instantáneamente

3. **Cocina inicia preparación**
   - Click en "INICIAR"
   - Estado cambia a PREPARING (azul)
   - Timestamp `preparing_at` se registra

4. **Pedido aparece en Pantalla Pública**
   - Sección "En Cocina" muestra #15
   - Cliente puede ver que su pedido está en preparación

5. **Cocina marca como listo**
   - Click en "LISTO"
   - Estado cambia a READY (verde)
   - Timestamp `ready_at` se registra
   - Sonido de notificación en pantalla pública

6. **Cliente ve su pedido listo**
   - Pedido #15 aparece grande en sección "¡Pedidos Listos!"
   - Animación pulse llama la atención

7. **Cliente recoge pedido**
   - Cajero marca como "PUEDE RECOGER" (DELIVERED)
   - Pedido desaparece de todas las pantallas
   - Timestamp `delivered_at` se registra

### Escenario: Cancelación de Pedido

1. **Necesidad de cancelar**
   - Click en botón X rojo en esquina de tarjeta
   - Modal de confirmación aparece

2. **Confirmación**
   - Usuario confirma cancelación
   - Estado cambia a CANCELLED
   - Timestamp `cancelled_at` se registra
   - Pedido desaparece con animación

---

## Configuración y Requisitos

### Requisitos del Sistema

1. **Modo Restaurante habilitado** en Business
2. **WebSocket configurado** (opcional pero recomendado)
3. **Navegador moderno** con soporte para:
   - CSS Grid
   - Flexbox
   - Fetch API
   - WebSocket
   - Web Audio API (para sonidos)

### Configuración del Negocio

```python
class Business(models.Model):
    # ... campos existentes ...
    business_mode = CharField(choices=[
        ('supermarket', 'Supermercado'),
        ('restaurant', 'Restaurante')
    ])
    enable_kds = BooleanField(default=False)
    enable_public_display = BooleanField(default=False)
    
    def supports_orders(self):
        return self.business_mode == 'restaurant'
```

### URLs

```python
# apps/ventas/urls_kds.py
urlpatterns = [
    path('kitchen/', views_kds.kds_view, name='kds'),
    path('kitchen/orders/', views_kds.kds_orders_json, name='kds_orders_json'),
    path('kitchen/order/<int:order_id>/update/', views_kds.kds_update_status, name='kds_update_status'),
    path('display/', views_kds.public_display_view, name='public_display'),
    path('display/orders/', views_kds.display_orders_json, name='display_orders_json'),
]
```

---

## Mejoras Implementadas

### Manejo de Errores
- ✅ Detección de sesión expirada
- ✅ Mensajes de error específicos del servidor
- ✅ Validación de transiciones de estado
- ✅ Manejo de órdenes sin items

### Optimizaciones de UX
- ✅ Modal de confirmación para cancelaciones
- ✅ Filtros que se mantienen al actualizar estados
- ✅ Órdenes nuevas aparecen con datos completos
- ✅ Orden cronológico correcto (más antiguo primero)
- ✅ Sin duplicados al recibir WebSocket
- ✅ Grid adaptativo sin scrollbar innecesario
- ✅ Tarjetas centradas cuando hay pocos pedidos

### Performance
- ✅ Actualización selectiva de órdenes (no recarga completa)
- ✅ Animaciones optimizadas con CSS
- ✅ Fetch de datos solo cuando es necesario
- ✅ WebSocket con reconexión automática

---

## Diferencias: Modo Restaurante vs Supermercado

| Característica | Restaurante | Supermercado |
|----------------|-------------|--------------|
| ID de Pedido | ✅ Visible | ❌ Oculto |
| Modelo Order | ✅ Se crea | ❌ No se crea |
| KDS | ✅ Disponible | ❌ No disponible |
| Pantalla Pública | ✅ Disponible | ❌ No disponible |
| Factura | Muestra #Pedido | Sin #Pedido |
| Venta Completa | Muestra #Pedido | Sin #Pedido |
| Transacciones | Muestra #Pedido | Sin #Pedido |
| Flujo | Pedido → Preparar → Entregar | Venta directa |

---

## Mantenimiento y Soporte

### Logs y Debugging

El sistema incluye logging en:
- Creación de órdenes
- Cambios de estado
- Errores de WebSocket
- Errores de actualización

### Monitoreo

Puntos clave a monitorear:
- Conexiones WebSocket activas
- Tiempo promedio por estado
- Órdenes canceladas (ratio)
- Órdenes pendientes antiguas (>30 min)

### Troubleshooting Común

**Problema:** Órdenes no aparecen en KDS
- Verificar que `enable_kds = True`
- Verificar que `business_mode = 'restaurant'`
- Revisar logs del servidor

**Problema:** WebSocket no conecta
- Verificar configuración de WebSocket en settings
- Verificar que el puerto esté abierto
- Revisar logs de conexión

**Problema:** Órdenes duplicadas
- Verificar que no haya múltiples listeners de WebSocket
- Revisar función `addNewOrderCard()` para verificación de existencia

---

## Futuras Mejoras Sugeridas

1. **Notificaciones Push** para dispositivos móviles
2. **Impresión automática** de tickets en cocina
3. **Estadísticas** de tiempo promedio por pedido
4. **Priorización** de pedidos urgentes
5. **Asignación** de pedidos a estaciones específicas
6. **Historial** de pedidos del día
7. **Reportes** de eficiencia de cocina
8. **Integración** con sistema de delivery
9. **Multi-idioma** para pantallas
10. **Temas personalizables** por negocio

---

## Conclusión

El sistema de órdenes para restaurantes transforma SouthernPOS en una solución completa para gestión de pedidos en tiempo real, mejorando la eficiencia operativa y la experiencia del cliente. La arquitectura modular permite activar/desactivar funcionalidades según las necesidades del negocio, manteniendo la simplicidad para negocios tipo supermercado.

---

**Versión:** 1.0  
**Última actualización:** 2025  
**Autor:** Equipo SouthernPOS
