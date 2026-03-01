# ⚙️ Configuración de IVA

## 📋 Descripción

El sistema de facturación electrónica usa la tasa de IVA configurada en el perfil del negocio, no un valor hardcodeado. Esto permite flexibilidad para diferentes países y cambios en la legislación tributaria.

## 🔧 Cómo Configurar el IVA

### Desde el Panel de Administración

1. Accede a **Configuraciones** en el menú
2. Busca el campo **Porcentaje de IVA**
3. Ingresa el porcentaje (ejemplo: 12, 15, 0)
4. Guarda los cambios

### Desde Django Admin

```python
from apps.usuarios.models import Business

# Obtener el negocio
business = Business.objects.get(user=usuario)

# Configurar IVA
business.iva_porcentaje = 15.00  # 15%
business.save()
```

## 📊 Tasas de IVA Soportadas

El sistema soporta las tasas oficiales del SRI de Ecuador:

| Porcentaje | Código SRI | Estado | Vigencia |
|------------|------------|--------|----------|
| 0% | 0 | Vigente | Productos exentos de IVA |
| 12% | 2 | Histórico | Tarifa general hasta marzo 2024 |
| 14% | 3 | Histórico | Incremento temporal post-terremoto 2016 |
| 15% | 4 | **VIGENTE** | **Tarifa general desde abril 2024** |

**✅ Actualización 2024**: 
- Desde abril 2024, la tarifa general de IVA en Ecuador es **15%**
- El código del SRI para 15% es **4**
- Las tarifas históricas (12%, 14%) se mantienen para documentos antiguos
- El sistema soporta múltiples tarifas según la fecha de emisión

## 🔄 Impacto en el Sistema

Cuando cambias el porcentaje de IVA, afecta:

### 1. Nuevas Ventas
- Se calculan con la nueva tasa automáticamente
- El desglose se hace correctamente

### 2. XML de Facturas Electrónicas
- Usa el porcentaje configurado
- Genera el código SRI correcto
- Calcula totales precisos

### 3. Reportes y UI
- Los templates muestran el porcentaje dinámicamente
- Ejemplo: "IVA (15%)" en lugar de "IVA (12%)"

## ⚠️ Ventas Existentes

**IMPORTANTE**: Cambiar el porcentaje de IVA NO afecta ventas ya registradas.

Las ventas existentes mantienen sus valores calculados al momento de la venta.

Si necesitas recalcular ventas antiguas (por ejemplo, si estaban mal calculadas):

```bash
# Esto usa la tasa actual del negocio para recalcular
python manage.py fix_venta_iva --dry-run
python manage.py fix_venta_iva
```

## 🌍 Configuración por País

### Ecuador (2024 - Actual)
```python
business.iva_porcentaje = 15.00  # Tarifa vigente desde abril 2024
```

### Ecuador - Productos Exentos
```python
business.iva_porcentaje = 0.00
```

### Ecuador - Histórico (2016-2024)
```python
business.iva_porcentaje = 12.00  # Tarifa general hasta marzo 2024
```

### Ecuador - Histórico (Post-terremoto 2016)
```python
business.iva_porcentaje = 14.00  # Incremento temporal
```

**Nota**: El sistema está diseñado específicamente para Ecuador y el SRI, con soporte completo para la tarifa vigente (15%) y tarifas históricas.

## 🔍 Verificación

Para verificar qué tasa está usando tu negocio:

```python
from apps.usuarios.models import Business

business = Business.objects.get(user=request.user)
print(f"IVA configurado: {business.iva_porcentaje}%")
```

## 📝 Ejemplo de Cálculo

Con IVA del 15% (tasa vigente en Ecuador desde abril 2024):

```
Producto: $23.00 (precio con IVA incluido)

Cálculo:
- Base = 23.00 / 1.15 = 20.00
- IVA = 23.00 - 20.00 = 3.00
- Total = 23.00

XML generado:
<totalSinImpuestos>20.00</totalSinImpuestos>
<totalImpuesto>
  <codigo>2</codigo>
  <codigoPorcentaje>4</codigoPorcentaje>  <!-- 4 = 15% según SRI -->
  <tarifa>15</tarifa>
  <baseImponible>20.00</baseImponible>
  <valor>3.00</valor>
</totalImpuesto>
<importeTotal>23.00</importeTotal>
```

## 🚨 Casos Especiales

### Productos con IVA 0%

Si vendes productos exentos de IVA, debes:
1. Configurar `iva_porcentaje = 0`
2. O implementar IVA por producto (feature futura)

### Cambio de Legislación

Si Ecuador cambia el IVA en el futuro:
1. Verifica que el SRI publique el nuevo código en su XSD oficial
2. Actualiza el método `_get_codigo_porcentaje()` en `xml_generator.py`
3. Actualiza el XSD local con el nuevo código
4. Actualiza `business.iva_porcentaje` con el nuevo valor
5. Las nuevas ventas usarán la nueva tasa
6. Las ventas antiguas mantienen su tasa original

## 🔒 Seguridad

- Solo administradores pueden cambiar el IVA
- Los cambios se registran en el historial
- No afecta retroactivamente las ventas

## 📚 Referencias

- [Tabla de códigos SRI Ecuador](https://www.sri.gob.ec/)
- [Especificaciones XML Factura Electrónica v1.1.0](https://www.sri.gob.ec/facturacion-electronica)
