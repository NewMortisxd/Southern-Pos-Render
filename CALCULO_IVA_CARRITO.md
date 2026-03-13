# Cálculo de IVA en el Carrito

## 🎯 Objetivo

Mostrar el desglose correcto del IVA en el carrito, ya que los productos tienen precios con IVA incluido.

## 📐 Fórmula de Cálculo

### Contexto
- Los productos ya tienen el IVA incluido en su precio
- Necesitamos extraer el IVA del precio total
- El porcentaje de IVA se obtiene de la configuración del usuario

### Fórmulas

```javascript
// Dado un precio CON IVA incluido:
precioConIva = $10.00
ivaPorcentaje = 15% (0.15)

// Calcular subtotal SIN IVA:
subtotalSinIva = precioConIva / (1 + ivaPorcentaje)
subtotalSinIva = 10.00 / (1 + 0.15)
subtotalSinIva = 10.00 / 1.15
subtotalSinIva = $8.70

// Calcular monto del IVA:
ivaAmount = precioConIva - subtotalSinIva
ivaAmount = 10.00 - 8.70
ivaAmount = $1.30

// Verificación:
subtotalSinIva + ivaAmount = precioConIva
8.70 + 1.30 = 10.00 ✓
```

## 🔧 Implementación

### 1. Backend (views.py)

```python
# Obtener IVA de la configuración del usuario
try:
    business = Business.objects.get(user=request.user)
    iva_porcentaje = business.iva_porcentaje
except Business.DoesNotExist:
    iva_porcentaje = 15  # Default 15% para Ecuador

# Pasar al template
context = {
    'iva_porcentaje': iva_porcentaje,
    # ... otros datos
}
```

### 2. Frontend (HTML)

```html
<div class="flex justify-between items-center mb-2">
    <span>Subtotal:</span>
    <span id="cart-subtotal">$0.00</span>
</div>
<div class="flex justify-between items-center mb-2">
    <span>IVA (<span id="iva-percentage">{{ iva_porcentaje }}</span>%):</span>
    <span id="cart-iva">$0.00</span>
</div>
<div class="flex justify-between items-center pt-3 border-t-2">
    <span>TOTAL:</span>
    <span id="cart-total">$0.00</span>
</div>
```

### 3. JavaScript (ventas_tactil.js)

```javascript
// Obtener porcentaje de IVA del template
const ivaPercentageElement = document.getElementById('iva-percentage');
const ivaPercentage = parseFloat(ivaPercentageElement.textContent);
const ivaTaxRate = ivaPercentage / 100; // 15 → 0.15

// En la función updateCart():
let total = 0; // Total con IVA incluido

cart.forEach(item => {
    total += item.price * item.quantity;
});

// Calcular subtotal sin IVA
const subtotalSinIva = total / (1 + ivaTaxRate);

// Calcular monto del IVA
const ivaAmount = total - subtotalSinIva;

// Actualizar display
document.getElementById('cart-subtotal').textContent = '$' + subtotalSinIva.toFixed(2);
document.getElementById('cart-iva').textContent = '$' + ivaAmount.toFixed(2);
document.getElementById('cart-total').textContent = '$' + total.toFixed(2);
```

## 📊 Ejemplo Práctico

### Carrito con 3 productos:

```
Producto 1: $10.00 (con IVA) × 2 = $20.00
Producto 2: $5.75 (con IVA) × 1 = $5.75
Producto 3: $8.50 (con IVA) × 3 = $25.50

Total con IVA: $51.25
```

### Cálculo (IVA 15%):

```javascript
totalConIva = 51.25
ivaTaxRate = 0.15

subtotalSinIva = 51.25 / 1.15 = 44.57
ivaAmount = 51.25 - 44.57 = 6.68

Verificación: 44.57 + 6.68 = 51.25 ✓
```

### Display en el carrito:

```
Subtotal:    $44.57
IVA (15%):   $ 6.68
─────────────────────
TOTAL:       $51.25
```

## 🌍 Configuración por País

El sistema es flexible para diferentes tasas de IVA:

### Ecuador (actual)
```
IVA: 15% (vigente desde abril 2024)
```

### Otros países (ejemplos)
```
Colombia: 19%
Perú: 18%
México: 16%
Chile: 19%
```

El porcentaje se configura en `Business.iva_porcentaje` y se aplica automáticamente.

## ✅ Ventajas de Este Enfoque

1. **Transparencia**: El cliente ve el desglose del IVA
2. **Cumplimiento**: Facilita la facturación electrónica
3. **Flexibilidad**: Se adapta a diferentes tasas de IVA
4. **Precisión**: Cálculo correcto desde precios con IVA incluido
5. **Auditoría**: Fácil verificar los montos

## 🔍 Validación

### Test Manual
```javascript
// Para IVA 15%:
precio = 115.00
subtotal = 115.00 / 1.15 = 100.00
iva = 115.00 - 100.00 = 15.00
verificación = 100.00 + 15.00 = 115.00 ✓

// Para IVA 12%:
precio = 112.00
subtotal = 112.00 / 1.12 = 100.00
iva = 112.00 - 100.00 = 12.00
verificación = 100.00 + 12.00 = 112.00 ✓
```

## 📝 Notas Importantes

1. **Redondeo**: Se usa `.toFixed(2)` para 2 decimales
2. **Precisión**: JavaScript maneja bien estos cálculos para montos típicos de POS
3. **Consistencia**: El mismo cálculo se usa en backend al guardar la venta
4. **Display**: El total siempre es el precio que paga el cliente (con IVA)

## 🎨 Mejoras Visuales

- Subtotal e IVA en texto normal
- Total en texto grande y verde (destacado)
- Separador visual entre IVA y Total
- Porcentaje de IVA visible para transparencia

## 🔄 Flujo Completo

1. Usuario agrega productos al carrito
2. JavaScript suma los precios (con IVA incluido)
3. Calcula subtotal sin IVA: `total / (1 + ivaTaxRate)`
4. Calcula IVA: `total - subtotal`
5. Muestra los 3 valores en el carrito
6. Al proceder al pago, estos valores se envían al backend
7. Backend valida y guarda en la base de datos

## ✅ Checklist de Implementación

- [x] Obtener IVA de configuración del usuario
- [x] Pasar IVA al template
- [x] Mostrar porcentaje de IVA en el carrito
- [x] Calcular subtotal sin IVA en JavaScript
- [x] Calcular monto de IVA
- [x] Mostrar desglose en el carrito
- [x] Mantener total como valor principal
- [x] Validar cálculos
- [x] Documentar fórmulas

## 🎯 Resultado Final

El carrito ahora muestra:
```
┌─────────────────────────┐
│ Subtotal:      $44.57   │
│ IVA (15%):     $ 6.68   │
│ ─────────────────────── │
│ TOTAL:         $51.25   │
└─────────────────────────┘
```

Transparente, preciso y profesional.
