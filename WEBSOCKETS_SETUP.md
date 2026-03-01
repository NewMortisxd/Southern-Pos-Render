# Configuración de WebSockets para Sistema de Órdenes

## Implementación Completada

Se ha implementado un sistema de actualizaciones en tiempo real usando Django Channels con WebSockets y Event-Driven Architecture (EDA).

## Características

✅ **WebSockets con reconexión automática**: Conexión persistente que se reconecta automáticamente si se pierde
✅ **Event-Driven Architecture**: Las señales de Django emiten eventos cuando cambian las órdenes
✅ **Actualizaciones instantáneas**: Sin necesidad de recargar la página
✅ **AJAX optimizado**: Actualizaciones de estado con feedback inmediato
✅ **Fallback inteligente**: Si WebSocket falla, el sistema sigue funcionando

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `channels>=4.0.0` - Framework de WebSockets para Django
- `channels-redis>=4.1.0` - Backend de Redis para producción
- `daphne>=4.0.0` - Servidor ASGI

### 2. Aplicar migraciones (si es necesario)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Ejecutar el servidor

**Para desarrollo (sin Redis):**
```bash
python manage.py runserver
```

O con Daphne:
```bash
daphne -b 0.0.0.0 -p 8000 southern_food_pos.asgi:application
```

**Para producción (con Redis):**

1. Instalar y ejecutar Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows
# Descargar desde https://github.com/microsoftarchive/redis/releases
```

2. Actualizar `settings.py` para usar Redis:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

3. Ejecutar con Daphne:
```bash
daphne -b 0.0.0.0 -p 8000 southern_food_pos.asgi:application
```

## Arquitectura

### Flujo de Eventos

```
1. Usuario actualiza estado de orden (KDS)
   ↓
2. Vista procesa la actualización (AJAX)
   ↓
3. Modelo Order se guarda
   ↓
4. Señal post_save se dispara
   ↓
5. Señal envía mensaje a Channel Layer
   ↓
6. Channel Layer distribuye a todos los WebSockets conectados
   ↓
7. Clientes reciben actualización instantánea
   ↓
8. UI se actualiza sin recargar
```

### Componentes

- **`asgi.py`**: Configuración ASGI con routing de WebSockets
- **`routing.py`**: Rutas WebSocket
- **`consumers.py`**: Manejadores de conexiones WebSocket
- **`signals.py`**: Emisores de eventos cuando cambian las órdenes
- **`apps.py`**: Registro de señales
- **Templates**: JavaScript con lógica de WebSocket y reconexión

## Uso

### Pantalla KDS (Cocina)

1. Navegar a `/kds/kitchen/`
2. La conexión WebSocket se establece automáticamente
3. Cuando se actualiza el estado de una orden:
   - El cambio se envía vía AJAX
   - WebSocket notifica a todas las pantallas conectadas
   - La UI se actualiza instantáneamente

### Pantalla Pública

1. Navegar a `/kds/display/`
2. La conexión WebSocket se establece automáticamente
3. Cuando una orden está lista:
   - Aparece automáticamente en la pantalla
   - Se reproduce un sonido de notificación
   - La animación llama la atención del cliente

## Optimizaciones Implementadas

1. **Reconexión automática**: Si se pierde la conexión, intenta reconectar hasta 5 veces
2. **Actualizaciones incrementales**: Solo se actualizan las cards que cambiaron
3. **Animaciones suaves**: Transiciones visuales para mejor UX
4. **Prefetch de datos**: Consultas optimizadas con `select_related` y `prefetch_related`
5. **Channel groups**: Cada negocio tiene su propio grupo de WebSocket

## Troubleshooting

### WebSocket no conecta

1. Verificar que el servidor esté corriendo con Daphne o `runserver`
2. Revisar la consola del navegador para errores
3. Verificar que `ALLOWED_HOSTS` incluya tu dominio

### Actualizaciones no aparecen

1. Verificar que las señales estén registradas (revisar `apps.py`)
2. Comprobar que Channel Layer esté configurado correctamente
3. Revisar logs del servidor para errores

### Problemas de rendimiento

1. Cambiar a Redis en producción (InMemoryChannelLayer es solo para desarrollo)
2. Optimizar consultas de base de datos
3. Considerar usar índices en campos frecuentemente consultados

## Deployment en Render.com

Agregar a `render.yaml`:

```yaml
services:
  - type: web
    name: southern-food-pos
    env: python
    buildCommand: "./build.sh"
    startCommand: "daphne -b 0.0.0.0 -p $PORT southern_food_pos.asgi:application"
    
  - type: redis
    name: southern-food-pos-redis
    ipAllowList: []
```

Y actualizar `settings.py`:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [config('REDIS_URL', default='redis://localhost:6379')],
        },
    },
}
```

## Próximos Pasos (Opcional)

- [ ] Agregar autenticación por token para WebSockets públicos
- [ ] Implementar heartbeat para detectar conexiones muertas
- [ ] Agregar métricas de rendimiento
- [ ] Implementar rate limiting
- [ ] Agregar tests para WebSockets

## Soporte

Para más información sobre Django Channels:
- Documentación oficial: https://channels.readthedocs.io/
- Tutorial: https://channels.readthedocs.io/en/stable/tutorial/
