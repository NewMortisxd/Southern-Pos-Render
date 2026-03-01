# Laboratorio de Facturación Electrónica SRI Ecuador

## 📋 Descripción

Este módulo proporciona un laboratorio interno para desarrolladores que permite generar y validar XMLs de facturas electrónicas según las especificaciones del SRI (Servicio de Rentas Internas) de Ecuador.

## 🎯 Propósito

El laboratorio es una herramienta de desarrollo que permite:
- Seleccionar ventas existentes del sistema
- Generar el XML de factura electrónica correspondiente
- Validar el XML contra el XSD oficial del SRI versión 1.1.0
- Visualizar errores de estructura detallados (línea, columna, mensaje)

**IMPORTANTE**: Este laboratorio NO firma digitalmente ni envía comprobantes al SRI. Es solo para validación estructural del XML.

## 🚀 Acceso

URL: `/electronic/lab/`

Requiere autenticación de usuario.

## 📁 Estructura del Módulo

```
apps/electronic_billing/
├── __init__.py
├── apps.py
├── urls.py
├── views_lab.py              # Vista principal del laboratorio
├── services/
│   ├── __init__.py
│   ├── xml_generator.py      # Generador de XML desde modelo Venta
│   └── xsd_validator.py      # Validador contra XSD del SRI
├── templates/
│   └── lab/
│       └── xml_lab.html      # Interfaz del laboratorio
└── README.md
```

## 🔧 Componentes

### 1. xml_generator.py

Genera XML de factura electrónica desde un objeto `Venta` de Django.

**Características**:
- Usa `lxml` para construcción correcta del XML (no concatenación de strings)
- Respeta el orden exacto de elementos requerido por el XSD del SRI
- Genera clave de acceso de 49 dígitos con algoritmo módulo 11
- Mapea tipos de identificación (RUC, Cédula, Pasaporte, Consumidor Final)
- Calcula impuestos (IVA 12%)

**Uso**:
```python
from apps.ventas.models import Venta
from apps.electronic_billing.services.xml_generator import InvoiceXMLGenerator

sale = Venta.objects.get(id=123)
generator = InvoiceXMLGenerator(sale)
xml_bytes = generator.generate()
```

### 2. xsd_validator.py

Valida XML contra el XSD oficial del SRI.

**Características**:
- Carga el XSD desde `schemas/factura_V1.1.0.xsd`
- Retorna errores detallados con línea, columna y mensaje
- Maneja errores de sintaxis XML y excepciones

**Uso**:
```python
from apps.electronic_billing.services.xsd_validator import validate_invoice_xml

is_valid, errors = validate_invoice_xml(xml_bytes)
if not is_valid:
    for error in errors:
        print(f"Línea {error['linea']}: {error['mensaje']}")
```

### 3. views_lab.py

Vista Django que orquesta el flujo completo:
1. Muestra dropdown con últimas 50 ventas
2. Al seleccionar una venta, genera su XML
3. Valida el XML contra el XSD
4. Muestra resultados con badge de estado y lista de errores

## 📝 Datos de Prueba

El generador usa datos de prueba para información tributaria:
- RUC: 1234567890001
- Razón Social: EMPRESA DE PRUEBA S.A.
- Ambiente: 1 (Pruebas)
- Establecimiento: 001
- Punto de Emisión: 001

**Para producción**, estos valores deben venir de la configuración del negocio.

## 💰 Manejo de IVA (CRÍTICO)

El sistema asume que **los precios incluyen IVA** (modelo B2C típico de Ecuador).

### Configuración de IVA

La tasa de IVA se obtiene de la configuración del negocio (`Business.iva_porcentaje`):
- **Por defecto: 15%** (Ecuador, vigente desde abril 2024)
- Configurable por usuario en el panel de configuración
- **Valores permitidos por SRI**: 0%, 12% (histórico), 14% (histórico), 15% (vigente)

El sistema soporta múltiples tarifas para manejar documentos históricos y la tarifa actual.

### Cálculo Correcto

Si un producto se vende en $23.00 (precio final) con IVA del 15%:

```python
# ❌ INCORRECTO
base = 23.00
iva = 23.00 * 0.15 = 3.45
total = 26.45  # ¡Error! El cliente pagó $23, no $26.45

# ✅ CORRECTO
tax_rate = business.iva_porcentaje / 100  # 0.15
base = 23.00 / (1 + tax_rate) = 20.00
iva = 23.00 - 20.00 = 3.00
total = 23.00  # Correcto
```

### Verificación Matemática

El XML debe cumplir:
```
totalSinImpuestos + totalConImpuestos.valor = importeTotal
```

Si esto no se cumple, el SRI rechaza la factura con:
```
ERROR EN CÁLCULO DE IMPUESTOS
EL VALOR TOTAL NO COINCIDE CON LA SUMA DE BASE + IMPUESTOS
```

### Implementación

El generador:
1. Recorre todos los items de la venta
2. Desglose cada subtotal: `base = subtotal / 1.12`
3. Calcula IVA: `iva = subtotal - base`
4. Acumula totales con redondeo correcto
5. Ajusta diferencias de redondeo (tolerancia ±2 centavos)

### Evitando Errores de Redondeo Acumulativo

**❌ Método incorrecto** (causa inconsistencias):
```python
# Calcular totales desde valores exactos
base_total_exact = sum(item.subtotal / 1.12 for item in items)
base_total = round(base_total_exact, 2)  # 31.24

# Pero cada línea se redondea individualmente
line1_base = round(18.99 / 1.12, 2)  # 16.96
line2_base = round(15.99 / 1.12, 2)  # 14.28
# Suma de líneas: 16.96 + 14.28 = 31.24

# ❌ Si usas base_total_exact redondeado, puede dar 31.23
# ❌ Inconsistencia: totalSinImpuestos ≠ sum(precioTotalSinImpuesto)
```

**✅ Método correcto** (usado en el generador):
```python
# 1. Redondear cada línea individualmente
line1_base = round(18.99 / 1.12, 2)  # 16.96
line2_base = round(15.99 / 1.12, 2)  # 14.28

# 2. Sumar las líneas REDONDEADAS
base_total = line1_base + line2_base  # 31.24

# 3. IVA = total_venta - base_total
iva_total = 34.98 - 31.24  # 3.74

# ✅ Garantiza: totalSinImpuestos == sum(precioTotalSinImpuesto)
```

**Regla del SRI**:
```
SUM(detalle.precioTotalSinImpuesto) DEBE SER IGUAL a totalSinImpuestos
```

Si no se cumple, el SRI rechaza con:
```
ERROR: INCONSISTENCIA EN TOTALES
LA SUMA DE LAS BASES NO COINCIDE CON EL TOTAL SIN IMPUESTOS
```

## 🔍 Validación XSD

El XSD incluido (`schemas/factura_V1.1.0.xsd`) es una versión funcional basada en las especificaciones del SRI versión 1.1.0.

**Elementos validados**:
- Estructura de `infoTributaria`
- Orden correcto de elementos en `infoFactura`
- Formato de fechas (dd/mm/yyyy)
- Longitud de RUC (13 dígitos)
- Clave de acceso (49 dígitos)
- Códigos de impuestos y porcentajes
- Estructura de detalles e impuestos

## 🎨 Interfaz

El laboratorio tiene un diseño dark mode moderno con:
- Dropdown para seleccionar ventas
- Badge de estado (✅ Válido / ❌ Inválido)
- Textarea con XML generado (monospace, resaltado)
- Botón para copiar XML al portapapeles
- Lista detallada de errores de validación
- Información de la venta seleccionada

## 🔄 Flujo de Trabajo

1. Usuario accede a `/electronic/lab/`
2. Selecciona una venta del dropdown
3. Presiona "Generar y Validar XML"
4. Sistema genera XML y valida contra XSD
5. Muestra resultado con XML y errores (si los hay)
6. Usuario puede copiar XML o seleccionar otra venta

## ⚙️ Instalación

1. Asegúrate de que `lxml` esté instalado:
```bash
pip install lxml>=4.9.0
```

2. Agrega la app a `INSTALLED_APPS` en `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'apps.electronic_billing',
]
```

3. Incluye las URLs en `urls.py`:
```python
path('electronic/', include(('apps.electronic_billing.urls', 'electronic_billing'), namespace='electronic_billing')),
```

4. **IMPORTANTE**: Corrige las ventas existentes que tienen IVA = 0:
```bash
# Ver qué se va a corregir (sin aplicar cambios)
python manage.py fix_venta_iva --dry-run

# Aplicar correcciones
python manage.py fix_venta_iva
```

Ver detalles en [MIGRACION_DATOS.md](MIGRACION_DATOS.md)

## 📚 Próximos Pasos

Este laboratorio es la base para implementar:
1. Firma digital de XMLs con certificado .p12
2. Envío de comprobantes al SRI (ambiente de pruebas y producción)
3. Recepción de autorizaciones
4. Generación de RIDE (Representación Impresa del Documento Electrónico)
5. Integración con flujo de ventas real

## 🐛 Troubleshooting

**Error: "No se encontró el archivo XSD"**
- Verifica que existe `schemas/factura_V1.1.0.xsd` en la raíz del proyecto

**Error: "Element 'X': This element is not expected"**
- El orden de elementos en el XML no coincide con el XSD
- Revisa `xml_generator.py` y asegúrate de seguir el orden exacto

**Error de importación de lxml**
- Instala lxml: `pip install lxml`
- En Windows puede requerir Visual C++ Build Tools

## 📄 Licencia

Parte del sistema Southern Food POS.
