# 📱 Acceso desde Android - Guía Rápida

## 🎯 Pasos Simples

### 1. En tu PC (Windows):

```cmd
run_local_network.bat
```

Verás algo como:
```
Tu IP local es: 192.168.1.100
Accede desde otros dispositivos en:
  http://192.168.1.100:8000
```

### 2. En tu Android:

1. Abre **Chrome** o **Firefox**
2. Ve a la URL que te mostró el script
3. Ejemplo: `http://192.168.1.100:8000`
4. ¡Listo! Usa la app normalmente

## ✅ Requisitos

- ✅ PC y Android en la **misma WiFi**
- ✅ Servidor corriendo en tu PC
- ✅ Puerto 8000 abierto (el script lo hace automático)

## 🔧 Si no funciona:

### Problema 1: No carga la página

**Solución:**
1. Verifica que ambos estén en la misma WiFi
2. Verifica que el servidor esté corriendo
3. Prueba desactivar el firewall temporalmente:
   ```cmd
   netsh advfirewall set allprofiles state off
   ```

### Problema 2: No sé mi IP

**Solución:**
```cmd
ipconfig
```
Busca "Dirección IPv4"

### Problema 3: Puerto ocupado

**Solución:**
```cmd
python manage.py runserver 0.0.0.0:8080
```
Luego accede a: `http://TU_IP:8080`

## 🎨 Interfaz Optimizada

La interfaz ya está optimizada para móviles:
- ✅ Botones grandes para dedos
- ✅ Scroll horizontal en chips
- ✅ Grid de 2 columnas
- ✅ Menú desplegable
- ✅ Sin zoom accidental en iOS

## 🔒 Seguridad

**IMPORTANTE:**
- ✅ Solo para desarrollo local
- ✅ Solo en tu WiFi privada
- ❌ NO expongas a internet público

## 💡 Tips

1. **Guarda la URL en favoritos** de tu Android
2. **Agrega a pantalla de inicio** para acceso rápido
3. **Usa modo pantalla completa** en el navegador
4. **Activa "Modo escritorio"** si necesitas ver más opciones

## 🚀 Ejemplo Completo

```
┌─────────────────────────────────────┐
│ PC (Windows)                        │
│ IP: 192.168.1.100                   │
│ Ejecuta: run_local_network.bat     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Android (Chrome)                    │
│ Misma WiFi                          │
│ Abre: http://192.168.1.100:8000    │
│ Login: tu usuario                   │
└─────────────────────────────────────┘
```

## 📞 Soporte

Si tienes problemas, revisa:
1. `EJECUTAR_EN_RED_LOCAL.md` - Guía completa
2. Firewall de Windows
3. Configuración de WiFi

¡Disfruta tu app desde Android! 📱✨
