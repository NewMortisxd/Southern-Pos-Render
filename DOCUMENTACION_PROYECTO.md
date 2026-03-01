# Southern Food POS - Documentación del Proyecto

## 📋 Descripción General

**Southern Food POS** es un sistema de punto de venta (Point of Sale) desarrollado en Django, diseñado para gestionar operaciones comerciales tanto en el sector de restaurantes como en retail/supermercados. El sistema permite administrar ventas, inventario, clientes, reportes financieros y configuraciones del negocio de manera integral.

### Características Principales
- Sistema multi-usuario con autenticación segura
- Dos modos de operación: Restaurante y Retail/Supermercado
- Gestión completa de inventario y productos
- Procesamiento de ventas con múltiples métodos de pago
- Generación de reportes financieros y fiscales
- Integración con Cloudinary para almacenamiento de imágenes
- Generación de facturas en formato PDF (tickets térmicos 80mm)
- Exportación de datos para el SRI (Servicio de Rentas Internas de Ecuador)

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico
- **Backend**: Django 4.2+ (Python 3.11)
- **Base de Datos**: PostgreSQL (Neon.tech)
- **Servidor Web**: Gunicorn
- **Archivos Estáticos**: WhiteNoise
- **Almacenamiento de Imágenes**: Cloudinary
- **Despliegue**: Render.com
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript

### Estructura de Aplicaciones

El proyecto está organizado en módulos Django independientes:

```
apps/
├── usuarios/          # Gestión de usuarios y autenticación
├── productos/         # Gestión de productos y categorías
├── ventas/           # Procesamiento de ventas y transacciones
├── clients/          # Gestión de clientes
├── transacciones/    # Registro de transacciones financieras
├── reportes/         # Generación de reportes y análisis
├── configuraciones/  # Configuración del negocio y personalización
└── core/             # Funcionalidades compartidas y middleware
```

---

## 📦 Módulos Implementados

### 1. **Usuarios** (`apps/usuarios/`)

**Estado**: ✅ Completamente Implementado

**Funcionalidades**:
- Registro de nuevos usuarios con información del negocio
- Autenticación mediante email y contraseña
- Modelo de usuario personalizado (`Usuario`) que extiende `AbstractUser`
- Modelo `Business` para almacenar configuración del negocio:
  - Información fiscal (RUC, IVA)
  - Datos de contacto (dirección, teléfono, email)
  - Logo del negocio
  - Modo de operación (restaurante/retail)
  - Personalización (colores, tema oscuro, nombre personalizado)
  - Configuración de facturas

**Archivos Clave**:
- `models.py`: Modelos `Usuario` y `Business`
- `views.py`: Login, registro, dashboard
- `middleware.py`: Control de acceso administrativo
- `context_processors.py`: Inyección de configuración del negocio en templates

---

### 2. **Productos** (`apps/productos/`)

**Estado**: ✅ Completamente Implementado

**Funcionalidades**:
- CRUD completo de productos
- Gestión de categorías de productos
- Campos del producto:
  - Nombre, precio, descripción
  - Stock (control de inventario)
  - Código de barras
  - Imagen (almacenada en Cloudinary)
  - Categoría
  - Usuario creador (multi-tenant)
- Búsqueda de productos por nombre, código de barras
- Filtrado por categoría
- Signal automático: Crea categoría "General" al registrar nuevo usuario

**Archivos Clave**:
- `models.py`: Modelos `Producto` y `Categoria`
- `views.py`: Vistas CRUD y búsqueda
- `forms.py`: Formularios de productos y categorías
- `signals.py`: Creación automática de categoría general
- `management/commands/crear_categorias_generales.py`: Comando para crear categorías

---

### 3. **Ventas** (`apps/ventas/`)

**Estado**: ✅ Completamente Implementado

**Funcionalidades**:
- **Dos interfaces de venta**:
  - Modo Restaurante: Vista tradicional con carrito
  - Modo Retail/Cajero: Vista optimizada para supermercados
- Carrito de compras dinámico (JavaScript)
- Procesamiento de ventas con:
  - Selección de productos
  - Cálculo automático de subtotal, IVA y total
  - Múltiples métodos de pago (efectivo, tarjeta, transferencia)
  - Cálculo de cambio para pagos en efectivo
- Asignación de cliente a la venta (opcional)
- Actualización automática de stock al completar venta
- Generación de facturas en PDF (formato ticket térmico 80mm)
- Historial de ventas
- Verificación de stock antes de procesar pago

**Modelos**:
- `Venta`: Encabezado de la venta (total, método de pago, cliente, fecha)
- `DetalleVenta`: Líneas de la venta (producto, cantidad, precio, subtotal)

**Archivos Clave**:
- `models.py`: Modelos de ventas
- `views.py`: Lógica de ventas, procesamiento de pagos, generación de PDF
- `templates/ventas/ventas.html`: Interfaz modo restaurante
- `templates/ventas/ventas_cajero.html`: Interfaz modo retail
- `templates/ventas/completar_venta.html`: Pantalla de checkout
- `templates/ventas/venta_completa.html`: Resumen de venta completada

---

### 4. **Clientes** (`apps/clients/`)

**Estado**: ✅ Completamente Implementado

**Funcionalidades**:
- CRUD completo de clientes
- Campos del cliente:
  - Código, nombre, razón social
  - Identificación (cédula/RUC)
  - Email, teléfono, dirección, ciudad
  - Grupo (regular, VIP, corporativo)
  - Estado (activo, inactivo, suspendido)
  - Crédito (días de plazo: 0, 15, 30, 45, 60, 90)
  - Cupo de crédito
  - Tasas de descuento y recargo
  - Notas y comentarios
- Búsqueda de clientes por nombre, identificación o código
- Filtrado por estado y grupo
- Asignación de clientes a ventas

**Archivos Clave**:
- `models.py`: Modelo `Cliente`
- `views.py`: CRUD y búsqueda de clientes
- `forms.py`: Formularios de clientes

---

### 5. **Transacciones** (`apps/transacciones/`)

**Estado**: ✅ Completamente Implementado

**Funcionalidades**:
- Registro automático de transacciones al completar ventas
- Generación de ID de transacción único
- Generación de número de factura secuencial por usuario
- Campos:
  - `transaction_id`: ID único global
  - `factuID`: Número secuencial por usuario
  - `venta`: Relación con la venta
  - `monto`: Monto de la transacción
  - `metodo_pago`: Método de pago utilizado
  - `fecha`: Fecha y hora de la transacción
  - `usuario_creador`: Usuario que realizó la transacción
  - `procesado_pago`: Estado del pago

**Archivos Clave**:
- `models.py`: Modelo `Transaccion` con lógica de generación de IDs

---

### 6. **Reportes** (`apps/reportes/`)

**Estado**: ✅ Parcialmente Implementado

**Funcionalidades Implementadas**:
- **Reporte de Ventas**:
  - Filtrado por rango de fechas
  - Filtrado por tipo de documento
  - Estadísticas: total de ventas, IVA, número de facturas
  - Gráfico de ventas por día
  - Comparación con período anterior
  - Paginación de resultados
  
- **Reporte de Inventario**:
  - Lista completa de productos
  - Productos con stock bajo (< 10 unidades)
  - Productos agotados
  - Valor total del inventario
  - Agrupación por categorías
  
- **Exportación de Datos**:
  - Generación de archivos XML para el SRI (ATS)
  - Estructura XML según normativa ecuatoriana
  - Incluye información de ventas, clientes, IVA

**Funcionalidades Pendientes** (Vistas creadas pero sin implementación completa):
- Reporte de IVA detallado
- Reporte de facturas y comprobantes
- Análisis de ventas avanzado
- Reporte de clientes
- Declaración del IVA (Formulario 104)
- Declaración del Impuesto a la Renta
- Productos más vendidos
- Reportes rápidos personalizados

**Archivos Clave**:
- `views.py`: Lógica de reportes y exportación
- `templates/reportes/`: Templates de reportes

---

### 7. **Configuraciones** (`apps/configuraciones/`)

**Estado**: ✅ Completamente Implementado

**Funcionalidades**:
- **Configuración del Negocio**:
  - Información básica (nombre, RUC, dirección, teléfono, email)
  - Logo del negocio
  - Configuración de IVA
  - Mensajes en facturas
  - Política de devolución
  
- **Personalización**:
  - Colores primarios y secundarios
  - Modo oscuro
  - Vista predeterminada (grid/lista)
  - Mostrar/ocultar imágenes de productos
  - Nombre de marca personalizado
  - Logo personalizado
  
- **Configuración de Cuenta**:
  - Actualización de datos personales
  - Cambio de contraseña
  - Información del negocio

**Funcionalidades Pendientes**:
- Gestión de usuarios (multi-usuario)
- Configuración del sistema
- Permisos y roles

**Archivos Clave**:
- `views.py`: Vistas de configuración
- `forms.py`: Formularios de configuración
- `models.py`: Modelo `BusinessConfiguration`

---

### 8. **Core** (`apps/core/`)

**Estado**: ✅ Implementado

**Funcionalidades**:
- Vistas compartidas (login, registro, dashboard)
- Middleware de control de acceso
- Páginas de error personalizadas (400, 403, 404, 500)

---

## 🔐 Seguridad

### Implementaciones de Seguridad
- Autenticación basada en Django Auth
- Protección CSRF en todos los formularios
- Filtrado de datos por usuario (multi-tenant)
- Conexiones HTTPS en producción
- Variables de entorno para datos sensibles (python-decouple)
- Sesiones seguras de Django
- Middleware de control de acceso administrativo
- Validación de entrada de datos
- Encriptación de contraseñas

### Configuración de Producción
- `DEBUG = False`
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = 'DENY'`

---

## 📊 Base de Datos

### Proveedor
- **PostgreSQL** en Neon.tech
- Conexión configurada mediante `DATABASE_URL`
- Soporte para SSL requerido

### Modelos Principales

#### Usuario
```python
- email (unique)
- nombre_completo
- direccion_negocio
- telefono_negocio
- ruc_negocio
- email_negocio
```

#### Business
```python
- user (OneToOne)
- nombre_negocio
- direccion_negocio
- telefono_negocio
- ruc_negocio
- email_negocio
- ciudad
- logo
- iva_porcentaje
- modo_operacion
- primary_color
- secondary_color
- dark_mode
- use_custom_brand_name
- custom_brand_name
```

#### Producto
```python
- nombre
- precio
- descripcion
- stock
- imagen (Cloudinary)
- codigo_barras
- categoria (FK)
- usuario_creador (FK)
- fecha_creacion
```

#### Categoria
```python
- nombre
- descripcion
- usuario_creador (FK)
```

#### Cliente
```python
- codigo
- nombre
- razon_social
- identificacion
- email
- telefono
- direccion
- ciudad
- grupo (regular/vip/corporativo)
- estado (activo/inactivo/suspendido)
- credito (días)
- cupo
- tasa_descuento
- tasa_recargo
- usuario_creador (FK)
```

#### Venta
```python
- usuario_creador (FK)
- cliente (FK, nullable)
- fecha_hora
- subtotal
- iva
- total
- metodo_pago (cash/card/transfer)
- monto_recibido
- cambio
```

#### DetalleVenta
```python
- venta (FK)
- producto (FK)
- cantidad
- precio_unitario
- subtotal
```

#### Transaccion
```python
- transaction_id (PK)
- factuID (secuencial por usuario)
- numero_factura_usuario
- venta (FK)
- monto
- metodo_pago
- fecha
- usuario_creador (FK)
- procesado_pago
```

---

## 🚀 Despliegue

### Plataforma
- **Render.com** (plan gratuito)
- Despliegue automático desde repositorio Git

### Configuración
- `build.sh`: Script de construcción (migraciones, collectstatic)
- `render.yaml`: Configuración de servicios
- `gunicorn_config.py`: Configuración del servidor WSGI
- `pre_deploy_check.py`: Verificaciones pre-despliegue

### Variables de Entorno Requeridas
```
SECRET_KEY=<django-secret-key>
DEBUG=False
DATABASE_URL=<postgresql-url>
CLOUDINARY_URL=<cloudinary-url>
ALLOWED_HOSTS=<domains>
```

### Limitaciones del Plan Gratuito
- La aplicación se "duerme" tras 15 minutos de inactividad
- Los archivos en `/media/` no persisten entre despliegues (se usa Cloudinary)
- Base de datos con límite de almacenamiento
- Backups de base de datos: 90 días

---

## 📁 Archivos Estáticos y Media

### Archivos Estáticos
- Servidos con **WhiteNoise** en producción
- Ubicación: `static/` y `staticfiles/`
- Incluye: CSS, JavaScript, imágenes del sistema

### Archivos Media (Uploads)
- **Cloudinary** para almacenamiento persistente
- Tipos de archivos:
  - Logos de negocios
  - Imágenes de productos
- Configuración en `settings.py` con `CLOUDINARY_URL`

---

## 🔄 Funcionalidades Pendientes de Implementar

### Reportes
- [ ] Reporte de IVA detallado con desglose
- [ ] Reporte de facturas y comprobantes completo
- [ ] Análisis de ventas avanzado (tendencias, predicciones)
- [ ] Reporte de clientes (historial de compras, deudas)
- [ ] Productos más vendidos con gráficos
- [ ] Reportes personalizados por usuario

### Configuraciones
- [ ] Gestión de usuarios múltiples
- [ ] Sistema de permisos y roles
- [ ] Configuración del sistema (backup, logs)
- [ ] Integración con servicios externos

### Ventas
- [ ] Ventas a crédito con seguimiento de pagos
- [ ] Devoluciones y notas de crédito
- [ ] Descuentos y promociones
- [ ] Propinas (modo restaurante)
- [ ] División de cuentas (modo restaurante)

### Productos
- [ ] Importación masiva de productos (CSV/Excel)
- [ ] Variantes de productos (tallas, colores)
- [ ] Productos compuestos (combos)
- [ ] Alertas de stock bajo automáticas
- [ ] Historial de cambios de precio

### Clientes
- [ ] Programa de puntos/fidelización
- [ ] Historial de compras detallado
- [ ] Gestión de deudas y pagos pendientes
- [ ] Envío de facturas por email
- [ ] Portal de cliente (auto-servicio)

### Integraciones
- [ ] Facturación electrónica (SRI Ecuador)
- [ ] Pasarelas de pago (PayPhone, Kushki)
- [ ] WhatsApp Business API
- [ ] Impresoras térmicas (ESC/POS)
- [ ] Lectores de código de barras

### Mejoras Generales
- [ ] Dashboard con métricas en tiempo real
- [ ] Notificaciones push
- [ ] Modo offline (PWA)
- [ ] App móvil (React Native/Flutter)
- [ ] Multi-sucursal
- [ ] Multi-idioma
- [ ] Temas personalizables avanzados

---

## 📝 Documentos Adicionales

### Documentación Existente
- `README_RENDER.md`: Guía de despliegue en Render
- `DEPLOYMENT_SUMMARY.md`: Resumen de despliegue
- `DEPLOY_CHECKLIST.md`: Lista de verificación pre-despliegue
- `LOCAL_DEVELOPMENT.md`: Guía de desarrollo local
- `MEDIA_FILES_INFO.md`: Información sobre archivos media
- `ERROR_PAGES_INFO.md`: Información sobre páginas de error
- `POLITICA_DE_PRIVACIDAD.txt`: Política de privacidad del sistema

---

## 🛠️ Comandos Útiles

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Crear categorías generales para todos los usuarios
python manage.py crear_categorias_generales

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar servidor de desarrollo
python manage.py runserver
```

### Producción
```bash
# Ejecutar con Gunicorn
gunicorn southern_food_pos.wsgi:application

# Verificaciones pre-despliegue
python pre_deploy_check.py

# Migrar imágenes a Cloudinary
python migrate_images_to_cloudinary.py
```

---

## 📞 Contacto y Soporte

Para consultas sobre el sistema:
- Email: [TU_EMAIL_DE_CONTACTO]
- Teléfono: [TU_TELÉFONO]

---

## 📄 Licencia

© 2025 Southern Food POS - Todos los derechos reservados

---

## 🔍 Notas Técnicas

### Arquitectura Multi-Tenant
El sistema implementa multi-tenancy a nivel de aplicación:
- Cada usuario tiene sus propios productos, categorías, clientes y ventas
- Filtrado automático por `usuario_creador` en todas las consultas
- Aislamiento de datos entre usuarios

### Cálculo de IVA
- IVA configurable por negocio (default: 15%)
- Los precios de productos incluyen IVA
- Cálculo: `subtotal = total / 1.15`, `iva = total - subtotal`

### Generación de Facturas
- Formato: PDF ticket térmico 80mm
- Librería: ReportLab
- Incluye: Logo, datos del negocio, cliente, productos, totales, QR placeholder
- Descarga automática al completar venta

### Exportación SRI
- Formato: XML según normativa ecuatoriana
- Incluye: ATS (Anexo Transaccional Simplificado)
- Datos: RUC, ventas, clientes, IVA, retenciones

---

**Última actualización**: Febrero 2025
**Versión del sistema**: 1.0.0
**Versión de Django**: 4.2+
**Versión de Python**: 3.11.0
