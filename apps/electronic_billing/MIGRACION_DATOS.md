# 🔄 Migración de Datos - Corrección de IVA

## ⚠️ Problema Identificado

Las ventas existentes en la base de datos tienen valores incorrectos:

```
subtotal = total_con_iva  (❌ Incorrecto)
iva = 0.00                (❌ Incorrecto)
total = total_con_iva     (✅ Correcto)
```

Esto causa inconsistencia entre:
- Lo que muestra la UI (IVA = 0)
- Lo que genera el XML de factura electrónica (IVA = 12%)

## ✅ Solución Implementada

Se corrigió el código en `apps/ventas/views.py` para que las **nuevas ventas** se guarden correctamente:

```python
# Precios incluyen IVA 12%
total_con_iva = suma_de_items
base_sin_iva = total_con_iva / 1.12
iva_calculado = total_con_iva - base_sin_iva

venta.subtotal = base_sin_iva   # Base sin IVA
venta.iva = iva_calculado       # IVA 12%
venta.total = total_con_iva     # Total que paga el cliente
```

## 🔧 Migración de Datos Existentes

Para corregir las ventas existentes, ejecuta este script:

```python
# Script de migración - ejecutar desde Django shell
# python manage.py shell

from apps.ventas.models import Venta
from decimal import Decimal

TAX_RATE = Decimal('0.12')

# Obtener todas las ventas con IVA = 0
ventas_incorrectas = Venta.objects.filter(iva=0)

print(f"Ventas a corregir: {ventas_incorrectas.count()}")

for venta in ventas_incorrectas:
    # El total es correcto (lo que pagó el cliente)
    total_con_iva = venta.total
    
    # Calcular base e IVA correctamente
    base_sin_iva = total_con_iva / (Decimal('1') + TAX_RATE)
    iva_calculado = total_con_iva - base_sin_iva
    
    # Redondear
    base_sin_iva = base_sin_iva.quantize(Decimal('0.01'))
    iva_calculado = iva_calculado.quantize(Decimal('0.01'))
    
    # Actualizar
    venta.subtotal = base_sin_iva
    venta.iva = iva_calculado
    venta.save()
    
    print(f"Venta #{venta.id}: Total ${total_con_iva} → Base ${base_sin_iva} + IVA ${iva_calculado}")

print("Migración completada")
```

## 📊 Ejemplo de Corrección

**Antes**:
```
Venta #123
subtotal: $34.98  (❌ incluye IVA)
iva:      $0.00   (❌ incorrecto)
total:    $34.98  (✅ correcto)
```

**Después**:
```
Venta #123
subtotal: $31.23  (✅ sin IVA)
iva:      $3.75   (✅ IVA 12%)
total:    $34.98  (✅ correcto)
```

## 🎯 Verificación

Después de la migración, verifica que:

```python
# Todas las ventas deben cumplir:
for venta in Venta.objects.all():
    assert venta.subtotal + venta.iva == venta.total
    print(f"✅ Venta #{venta.id} OK")
```

## 📝 Notas Importantes

1. **No afecta el total cobrado**: El campo `total` siempre fue correcto
2. **Solo corrige la presentación**: Ahora subtotal e IVA se muestran correctamente
3. **Compatibilidad con SRI**: Los XMLs ahora coinciden con los datos guardados
4. **Ejecutar una sola vez**: El script es idempotente pero no es necesario ejecutarlo múltiples veces

## 🔒 Backup Recomendado

Antes de ejecutar la migración:

```bash
# PostgreSQL
pg_dump -U usuario -d nombre_db -t ventas_venta > backup_ventas.sql

# O desde Django
python manage.py dumpdata ventas.Venta > backup_ventas.json
```

## ⏰ Cuándo Ejecutar

- **Desarrollo**: Inmediatamente
- **Producción**: En ventana de mantenimiento
- **Tiempo estimado**: < 1 segundo por cada 1000 ventas
