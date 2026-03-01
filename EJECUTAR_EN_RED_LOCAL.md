# 🌐 Cómo ejecutar el servidor en tu red local

## 🚀 Método Rápido (Recomendado)

### Usa el script automático:

```cmd
run_local_network.bat
```

Este script:
- ✅ Detecta automáticamente tu IP local
- ✅ Inicia el servidor en `0.0.0.0:8000`
- ✅ Te muestra la URL para acceder desde otros dispositivos

**Ejemplo de salida:**
```
Tu IP local es: 192.168.1.100
Accede desde otros dispositivos en:
  http://192.168.1.100:8000
```

Luego desde tu **Android/tablet**, abre el navegador y ve a esa URL.

---

## 📱 Método Manual

### Pasos para acceder desde cualquier dispositivo en tu casa

### 1. Obtener tu dirección IP local

En Windows, abre CMD o PowerShell y ejecuta:
```cmd
ipconfig
```

Busca la línea que dice "Dirección IPv4" (generalmente algo como `192.168.1.X` o `192.168.0.X`)

### 2. Ejecutar el servidor Django

**IMPORTANTE: En Windows NO uses Gunicorn** (no es compatible). Usa el servidor de desarrollo de Django:

```cmd
python manage.py runserver 0.0.0.0:8000
```

El `0.0.0.0` hace que el servidor escuche en todas las interfaces de red, no solo en localhost.

**Si tienes WebSockets (para KDS o pantallas públicas), usa Daphne en su lugar:**

```cmd
daphne -b 0.0.0.0 -p 8000 southern_food_pos.asgi:application
```

### 3. Acceder desde otros dispositivos

Desde cualquier dispositivo en tu misma red WiFi, abre el navegador y ve a:

```
http://TU_IP_LOCAL:8000
```

Por ejemplo, si tu IP es `192.168.1.100`:
```
http://192.168.1.100:8000
```

### 4. Verificar el firewall de Windows

Si no puedes conectarte, es posible que el firewall de Windows esté bloqueando la conexión. Para permitirlo:

1. Abre "Firewall de Windows Defender"
2. Click en "Configuración avanzada"
3. Click en "Reglas de entrada"
4. Click en "Nueva regla..."
5. Selecciona "Puerto" y click "Siguiente"
6. Selecciona "TCP" y escribe "8000" en puertos específicos
7. Selecciona "Permitir la conexión"
8. Marca todas las opciones (Dominio, Privado, Público)
9. Dale un nombre como "Django Development Server"

### 5. Para WebSockets (KDS y pantallas públicas)

Si usas funcionalidades con WebSockets, asegúrate de que los dispositivos puedan conectarse usando:

```
ws://TU_IP_LOCAL:8000/ws/...
```

## Notas importantes

- Todos los dispositivos deben estar en la misma red WiFi
- Esta configuración es solo para desarrollo local, NO para producción
- El servidor debe estar ejecutándose en tu PC para que otros dispositivos puedan acceder
- Si cambias de red o tu router te asigna una IP diferente, tendrás que usar la nueva IP
- **Gunicorn NO funciona en Windows** - usa `python manage.py runserver` o `daphne` en su lugar

## Ejemplo completo

Si tu IP es `192.168.1.100`:

1. En tu PC ejecuta: `python manage.py runserver 0.0.0.0:8000`
2. En tu celular/tablet abre: `http://192.168.1.100:8000`
3. ¡Listo! Deberías ver tu aplicación

## Solución de problemas

### No puedo conectarme desde otro dispositivo

1. Verifica que ambos dispositivos estén en la misma red WiFi
2. Verifica que el servidor esté corriendo con `0.0.0.0:8000`
3. Verifica tu IP con `ipconfig`
4. Desactiva temporalmente el firewall para probar
5. Intenta hacer ping desde el otro dispositivo: `ping TU_IP_LOCAL`

### Los WebSockets no funcionan

Asegúrate de que en tu código JavaScript, las URLs de WebSocket usen la IP correcta:
```javascript
const ws = new WebSocket('ws://192.168.1.100:8000/ws/...');
```

O mejor aún, usa una URL relativa que se adapte automáticamente:
```javascript
const ws = new WebSocket(`ws://${window.location.host}/ws/...`);
```
