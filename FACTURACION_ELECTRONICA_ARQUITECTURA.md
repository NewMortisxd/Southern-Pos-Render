# 🧾 ARQUITECTURA DE FACTURACIÓN ELECTRÓNICA - ECUADOR SRI

## 📋 Problema a Resolver

En Ecuador, el SRI requiere que las facturas electrónicas tengan un número con estructura específica:

```
001-001-000000001
│   │   └─ Secuencial (9 dígitos)
│   └───── Punto de Emisión (3 dígitos)
└───────── Establecimiento (3 dígitos)
```

## ❌ ERROR COMÚN (NO HACER)

```python
# ❌ MAL - Usar el ID de la base de datos
numero_factura = f"001-001-{venta.id:09d}"
```

**Problemas:**
- Si borras registros → rompe secuencia
- Si migras datos → rompe secuencia
- Si tienes varios establecimientos → imposible manejar
- El ID no es contable
- No cumple con SRI

## ✅ SOLUCIÓN PROFESIONAL

### 1. Modelo Business (Ya existe, mejorar)

```python
class Business(models.Model):
    # ... campos existentes ...
    
    # Facturación Electrónica SRI
    establecimiento = models.CharField(
        max_length=3,
        default='001',
        verbose_name="Establecimiento",
        help_text="3 dígitos (ej: 001)"
    )
    punto_emision = models.CharField(
        max_length=3,
        default='001',
        verbose_name="Punto de Emisión",
        help_text="3 dígitos (ej: 001)"
    )
    secuencial_actual = models.PositiveIntegerField(
        default=1,
        verbose_name="Secuencial Actual de Facturación",
        help_text="Se autoincrementa con cada factura"
    )
```

### 2. Modelo Venta (Agregar campos)

```python
class Venta(models.Model):
    # ... campos existentes ...
    
    # 🎯 FACTURACIÓN ELECTRÓNICA
    establecimiento_codigo = models.CharField(
        max_length=3,
        default='001',
        verbose_name="Código Establecimiento"
    )
    punto_emision_codigo = models.CharField(
        max_length=3,
        default='001',
        verbose_name="Código Punto Emisión"
    )
    secuencial = models.PositiveIntegerField(
        verbose_name="Número Secuencial",
        help_text="Secuencial único de esta factura"
    )
    numero_factura = models.CharField(
        max_length=17,
        unique=True,
        verbose_name="Número de Factura",
        help_text="Formato: 001-001-000000001"
    )
    
    # Facturación electrónica
    clave_acceso = models.CharField(
        max_length=49,
        blank=True,
        null=True,
        verbose_name="Clave de Acceso SRI"
    )
    fecha_autorizacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Autorización SRI"
    )
    estado_sri = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('AUTORIZADA', 'Autorizada'),
            ('RECHAZADA', 'Rechazada'),
            ('NO_AUTORIZADA', 'No Autorizada'),
        ],
        default='PENDIENTE',
        verbose_name="Estado SRI"
    )
```

## 🔥 FLUJO DE GENERACIÓN DE FACTURA

### Paso 1: Al crear una venta

```python
from django.db import transaction

@transaction.atomic
def crear_venta_con_factura(usuario, cliente, items, metodo_pago):
    # 1. Obtener configuración del negocio
    business = Business.objects.select_for_update().get(user=usuario)
    
    # 2. Obtener datos de facturación
    establecimiento = business.establecimiento
    punto_emision = business.punto_emision
    secuencial = business.secuencial_actual
    
    # 3. Generar número de factura
    numero_factura = f"{establecimiento}-{punto_emision}-{secuencial:09d}"
    
    # 4. Crear la venta
    venta = Venta.objects.create(
        usuario_creador=usuario,
        cliente=cliente,
        establecimiento_codigo=establecimiento,
        punto_emision_codigo=punto_emision,
        secuencial=secuencial,
        numero_factura=numero_factura,
        metodo_pago=metodo_pago,
        # ... otros campos ...
    )
    
    # 5. Incrementar secuencial (CRÍTICO)
    business.secuencial_actual = F('secuencial_actual') + 1
    business.save(update_fields=['secuencial_actual'])
    
    # 6. Crear detalles de venta
    for item in items:
        DetalleVenta.objects.create(
            venta=venta,
            producto=item['producto'],
            cantidad=item['cantidad'],
            # ... otros campos ...
        )
    
    return venta
```

### Paso 2: Generar XML para SRI

```python
def generar_xml_factura(venta):
    """Genera XML según especificaciones SRI"""
    business = venta.usuario_creador.business
    
    xml_data = {
        'infoTributaria': {
            'ambiente': business.ambiente_sri,
            'tipoEmision': business.tipo_emision,
            'razonSocial': business.razon_social_legal,
            'ruc': business.ruc_negocio,
            'claveAcceso': generar_clave_acceso(venta),
            'codDoc': '01',  # 01 = Factura
            'estab': venta.establecimiento_codigo,
            'ptoEmi': venta.punto_emision_codigo,
            'secuencial': f"{venta.secuencial:09d}",
            'dirMatriz': business.direccion_negocio,
        },
        'infoFactura': {
            'fechaEmision': venta.fecha_hora.strftime('%d/%m/%Y'),
            'totalSinImpuestos': str(venta.subtotal),
            'totalConImpuestos': str(venta.total),
            # ... más campos ...
        },
        'detalles': [
            {
                'descripcion': detalle.nombre_producto,
                'cantidad': str(detalle.cantidad),
                'precioUnitario': str(detalle.precio_unitario),
                'precioTotalSinImpuesto': str(detalle.subtotal),
            }
            for detalle in venta.detalleventa_set.all()
        ]
    }
    
    return generar_xml_sri(xml_data)
```

## 🎯 MIGRACIÓN NECESARIA

```python
# apps/ventas/migrations/0003_add_facturacion_electronica.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('ventas', '0002_add_order_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='establecimiento_codigo',
            field=models.CharField(default='001', max_length=3, verbose_name='Código Establecimiento'),
        ),
        migrations.AddField(
            model_name='venta',
            name='punto_emision_codigo',
            field=models.CharField(default='001', max_length=3, verbose_name='Código Punto Emisión'),
        ),
        migrations.AddField(
            model_name='venta',
            name='secuencial',
            field=models.PositiveIntegerField(null=True, blank=True, verbose_name='Número Secuencial'),
        ),
        migrations.AddField(
            model_name='venta',
            name='numero_factura',
            field=models.CharField(max_length=17, null=True, blank=True, unique=True, verbose_name='Número de Factura'),
        ),
        migrations.AddField(
            model_name='venta',
            name='clave_acceso',
            field=models.CharField(max_length=49, blank=True, null=True, verbose_name='Clave de Acceso SRI'),
        ),
        migrations.AddField(
            model_name='venta',
            name='fecha_autorizacion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Autorización SRI'),
        ),
        migrations.AddField(
            model_name='venta',
            name='estado_sri',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('PENDIENTE', 'Pendiente'),
                    ('AUTORIZADA', 'Autorizada'),
                    ('RECHAZADA', 'Rechazada'),
                    ('NO_AUTORIZADA', 'No Autorizada'),
                ],
                default='PENDIENTE',
                verbose_name='Estado SRI'
            ),
        ),
    ]
```

## 📊 CASOS DE USO

### Caso 1: Negocio con un solo punto de venta
```
Establecimiento: 001
Punto Emisión: 001
Secuencial: 1, 2, 3, 4...

Facturas:
001-001-000000001
001-001-000000002
001-001-000000003
```

### Caso 2: Negocio con múltiples sucursales
```
Sucursal A:
  Establecimiento: 001
  Punto Emisión: 001
  Secuencial: 1, 2, 3...

Sucursal B:
  Establecimiento: 002
  Punto Emisión: 001
  Secuencial: 1, 2, 3...
```

Cada sucursal tiene su propio secuencial independiente.

### Caso 3: Múltiples cajas en una sucursal
```
Caja 1:
  Establecimiento: 001
  Punto Emisión: 001
  Secuencial: 1, 2, 3...

Caja 2:
  Establecimiento: 001
  Punto Emisión: 002
  Secuencial: 1, 2, 3...
```

## 🚨 REGLAS CRÍTICAS

1. ✅ **NUNCA usar venta.id como secuencial**
2. ✅ **Usar transacciones atómicas** al generar facturas
3. ✅ **select_for_update()** al obtener secuencial
4. ✅ **Guardar número_factura como campo fijo**, no calcularlo dinámicamente
5. ✅ **Incrementar secuencial DESPUÉS de crear la venta**
6. ✅ **Validar formato antes de guardar**

## 🔧 FUNCIONES AUXILIARES

```python
def generar_clave_acceso(venta):
    """
    Genera clave de acceso de 49 dígitos según SRI
    Formato: DDMMYYYYTTCCCCCCCCCRRRRRRRRRRCDE
    """
    business = venta.usuario_creador.business
    fecha = venta.fecha_hora.strftime('%d%m%Y')
    tipo_comprobante = '01'  # Factura
    ruc = business.ruc_negocio
    ambiente = business.ambiente_sri
    serie = f"{venta.establecimiento_codigo}{venta.punto_emision_codigo}"
    secuencial = f"{venta.secuencial:09d}"
    codigo_numerico = '12345678'  # Generar aleatoriamente
    tipo_emision = business.tipo_emision
    
    clave_sin_digito = (
        fecha + tipo_comprobante + ruc + ambiente + 
        serie + secuencial + codigo_numerico + tipo_emision
    )
    
    digito_verificador = calcular_digito_verificador_modulo11(clave_sin_digito)
    
    return clave_sin_digito + str(digito_verificador)


def calcular_digito_verificador_modulo11(clave):
    """Calcula dígito verificador según algoritmo módulo 11 del SRI"""
    factor = 7
    suma = 0
    
    for digito in clave:
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    
    residuo = suma % 11
    digito = 11 - residuo if residuo != 0 else 0
    
    return 0 if digito == 11 else digito
```

## 📈 BENEFICIOS DE ESTA ARQUITECTURA

1. ✅ **Cumplimiento SRI** - Estructura correcta de facturación
2. ✅ **Escalable** - Soporta múltiples sucursales y cajas
3. ✅ **Auditable** - Secuencial no se puede alterar
4. ✅ **Robusto** - Transacciones atómicas previenen duplicados
5. ✅ **Profesional** - Separación clara de responsabilidades
6. ✅ **Migratable** - Datos históricos preservados

## 🚀 PRÓXIMOS PASOS

1. Crear migración para agregar campos a Venta
2. Actualizar vista de crear venta para generar número de factura
3. Implementar generación de XML SRI
4. Crear servicio de envío a SRI
5. Implementar RIDE (Representación Impresa del Documento Electrónico)

---

**Fecha:** 2026-03-04  
**Estado:** 📝 Documentado - Listo para implementar  
**Prioridad:** 🔥 CRÍTICA - Base para facturación electrónica
