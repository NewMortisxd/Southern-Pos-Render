# 🏗️ ARQUITECTURA DE VENTAS Y TRANSACCIONES - LEMON POS

## 📋 Índice
1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [Modelos de Datos](#modelos-de-datos)
3. [Flujo de Ventas](#flujo-de-ventas)
4. [Sistema de Descuentos y Recargos](#sistema-de-descuentos-y-recargos)
5. [Crédito y Pagos](#crédito-y-pagos)
6. [Reportes](#reportes)

---

## 1️⃣ CONCEPTOS FUNDAMENTALES

### Diferencia entre Venta y Transacción

#### 🛒 VENTA
**Definición:** Operación comercial completa

**Incluye:**
- Productos vendidos
- Cliente
- Impuestos (IVA)
- Descuentos
- Recargos
- Total a pagar

**Ejemplo:**
```
Venta #1024
Cliente: Juan Pérez
Productos: $50.00
IVA (15%): $7.50
Descuento: -$2.00
Total: $55.50
```

#### 💰 TRANSACCIÓN
**Definición:** Movimiento de dinero

**Tipos:**
- Pago de venta (efectivo, tarjeta, transferencia)
- Pago de crédito
- Devolución
- Abono a cuenta

**Ejemplo:**
```
Transacción #5678
Tipo: pago_venta
Método: efectivo
Monto pagado: $60.00
Cambio: $4.50
```

---

## 2️⃣ MODELOS DE DATOS

### 📊 Modelo: Venta

```python
class Venta(models.Model):
    # === IDENTIFICACIÓN ===
    id = AutoField(primary_key=True)
    numero_factura = CharField()  # Secuencial por usuario
    usuario_creador = ForeignKey(Usuario)
    caja = ForeignKey(Caja, null=True)  # Futuro
    fecha_hora = DateTimeField(auto_now_add=True)
    
    # === CLIENTE ===
    cliente = ForeignKey(Cliente, null=True, blank=True)
    tipo_cliente = CharField(choices=[
        ('final', 'Consumidor Final'),
        ('registrado', 'Cliente Registrado'),
        ('con_datos', 'Con Datos Manuales')
    ])
    
    # === TOTALES ===
    subtotal = DecimalField()  # Suma de productos sin IVA
    descuento_total = DecimalField(default=0)  # Descuentos aplicados
    recargo_total = DecimalField(default=0)  # Recargos aplicados
    iva = DecimalField()  # Impuesto calculado
    total = DecimalField()  # Total final a pagar
    
    # === PAGO ===
    metodo_pago = CharField(choices=[
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('credit', 'Crédito')
    ])
    monto_recibido = DecimalField(null=True)  # Solo para efectivo
    cambio = DecimalField(null=True)  # Solo para efectivo
    
    # === ESTADO ===
    estado_pago = CharField(choices=[
        ('pendiente', 'Pendiente'),
        ('parcial', 'Pago Parcial'),
        ('pagado', 'Pagado Completo')
    ], default='pagado')
    saldo_pendiente = DecimalField(default=0)  # Para crédito
    
    # === FACTURACIÓN ===
    tipo_comprobante = CharField(choices=[
        ('ticket', 'Ticket'),
        ('factura', 'Factura Electrónica'),
        ('nota_venta', 'Nota de Venta')
    ], default='ticket')
    
    # === FACTURACIÓN ELECTRÓNICA SRI ===
    punto_emision = ForeignKey(PuntoEmision, null=True)
    establecimiento_codigo = CharField()
    secuencial = CharField()
    clave_acceso = CharField(null=True)
    estado_sri = CharField(null=True)
    
    # === MODO RESTAURANTE ===
    order = ForeignKey(Order, null=True)  # Relación con orden
```

### 📦 Modelo: DetalleVenta

```python
class DetalleVenta(models.Model):
    # === RELACIONES ===
    venta = ForeignKey(Venta, on_delete=CASCADE)
    producto = ForeignKey(Producto, on_delete=PROTECT)
    
    # === CANTIDADES ===
    cantidad = DecimalField()
    precio_unitario = DecimalField()  # Precio al momento de venta
    
    # === DESCUENTOS ===
    descuento_porcentaje = DecimalField(default=0)  # % de descuento
    descuento_monto = DecimalField(default=0)  # Monto en $
    
    # === TOTALES ===
    subtotal = DecimalField()  # cantidad * precio_unitario - descuento
    
    # === IMPUESTOS ===
    aplica_iva = BooleanField(default=True)
    porcentaje_iva = DecimalField(default=15)
    
    # === METADATA ===
    notas = TextField(null=True)  # Notas especiales del producto
```

### 💳 Modelo: Transaccion

```python
class Transaccion(models.Model):
    # === IDENTIFICACIÓN ===
    transaction_id = PositiveIntegerField(primary_key=True)  # ID global único
    factuID = PositiveIntegerField()  # ID secuencial por usuario
    numero_factura_usuario = PositiveIntegerField()  # Compatibilidad
    
    # === RELACIONES ===
    venta = ForeignKey(Venta, on_delete=CASCADE, null=True)
    usuario_creador = ForeignKey(Usuario, on_delete=CASCADE)
    cliente = ForeignKey(Cliente, null=True)  # Para pagos de crédito
    
    # === TIPO Y MÉTODO ===
    tipo_transaccion = CharField(choices=[
        ('venta', 'Pago de Venta'),
        ('pago_credito', 'Pago de Crédito'),
        ('devolucion', 'Devolución'),
        ('abono', 'Abono a Cuenta')
    ], default='venta')
    
    metodo_pago = CharField(choices=[
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('credit', 'Crédito')
    ])
    
    # === MONTOS ===
    monto = DecimalField()  # Monto de la transacción
    
    # === METADATA ===
    fecha = DateTimeField(auto_now_add=True)
    procesado_pago = BooleanField(default=False)
    referencia = CharField(null=True)  # Número de referencia bancaria
    notas = TextField(null=True)
```

---

## 3️⃣ FLUJO DE VENTAS

### Paso a Paso

#### 1️⃣ Cajero agrega productos
```python
# Se crean registros en DetalleVenta
detalle = DetalleVenta.objects.create(
    venta=venta,
    producto=producto,
    cantidad=2,
    precio_unitario=10.00,
    subtotal=20.00
)
```

#### 2️⃣ Selecciona cliente
```python
# Sistema aplica descuentos/recargos del cliente
if cliente.tasa_descuento > 0:
    venta.descuento_total += (subtotal * cliente.tasa_descuento / 100)

if cliente.tasa_recargo > 0:
    venta.recargo_total += (subtotal * cliente.tasa_recargo / 100)
```

#### 3️⃣ Sistema calcula totales
```python
# Cálculo automático
subtotal = sum(detalle.subtotal for detalle in detalles)
subtotal_con_descuentos = subtotal - venta.descuento_total + venta.recargo_total
iva = subtotal_con_descuentos * 0.15
total = subtotal_con_descuentos + iva

venta.subtotal = subtotal
venta.iva = iva
venta.total = total
venta.save()
```

#### 4️⃣ Cajero elige método de pago
```python
# Opciones: cash, card, transfer, credit
venta.metodo_pago = 'cash'
venta.monto_recibido = 60.00
venta.cambio = 60.00 - venta.total
```

#### 5️⃣ Se crea la venta
```python
venta.estado_pago = 'pagado'
venta.saldo_pendiente = 0
venta.save()
```

#### 6️⃣ Se crea la transacción
```python
transaccion = Transaccion.objects.create(
    venta=venta,
    tipo_transaccion='venta',
    metodo_pago='cash',
    monto=venta.total,
    usuario_creador=request.user
)
```

---

## 4️⃣ SISTEMA DE DESCUENTOS Y RECARGOS

### Niveles de Descuento

#### 1️⃣ Descuento por Producto
**Aplicación:** En el detalle de venta
```python
detalle.descuento_porcentaje = 10  # 10% off
detalle.descuento_monto = precio_unitario * 0.10
detalle.subtotal = (precio_unitario - descuento_monto) * cantidad
```

#### 2️⃣ Descuento por Cliente
**Aplicación:** Al subtotal de la venta
```python
if cliente.tasa_descuento > 0:
    descuento_cliente = subtotal * (cliente.tasa_descuento / 100)
    venta.descuento_total += descuento_cliente
```

#### 3️⃣ Descuento Manual
**Aplicación:** Por el cajero
```python
# Cajero aplica descuento de $5
venta.descuento_total += 5.00
```

### Recargos

Funcionan igual pero sumando:
```python
if cliente.tasa_recargo > 0:
    recargo_cliente = subtotal * (cliente.tasa_recargo / 100)
    venta.recargo_total += recargo_cliente
```

---

## 5️⃣ CRÉDITO Y PAGOS

### Venta a Crédito

```python
# Al crear la venta
venta.metodo_pago = 'credit'
venta.estado_pago = 'pendiente'
venta.saldo_pendiente = venta.total

# Transacción de crédito
transaccion = Transaccion.objects.create(
    venta=venta,
    tipo_transaccion='venta',
    metodo_pago='credit',
    monto=0,  # No se paga nada aún
    usuario_creador=request.user
)
```

### Pago Posterior

```python
# Cliente paga $20 de su deuda
transaccion = Transaccion.objects.create(
    venta=venta,
    cliente=cliente,
    tipo_transaccion='pago_credito',
    metodo_pago='cash',
    monto=20.00,
    usuario_creador=request.user
)

# Actualizar saldo
venta.saldo_pendiente -= 20.00
if venta.saldo_pendiente == 0:
    venta.estado_pago = 'pagado'
elif venta.saldo_pendiente < venta.total:
    venta.estado_pago = 'parcial'
venta.save()
```

---

## 6️⃣ REPORTES

### Ventas por Día
```python
ventas_hoy = Venta.objects.filter(
    fecha_hora__date=today,
    usuario_creador=user
).aggregate(
    total=Sum('total'),
    cantidad=Count('id')
)
```

### Ventas por Cajero
```python
ventas_por_usuario = Venta.objects.filter(
    fecha_hora__range=[inicio, fin]
).values('usuario_creador__username').annotate(
    total=Sum('total'),
    cantidad=Count('id')
)
```

### Clientes con Deuda
```python
clientes_deuda = Venta.objects.filter(
    saldo_pendiente__gt=0,
    usuario_creador=user
).values('cliente__nombre').annotate(
    deuda_total=Sum('saldo_pendiente')
)
```

### Métodos de Pago
```python
por_metodo = Transaccion.objects.filter(
    fecha__date=today,
    usuario_creador=user
).values('metodo_pago').annotate(
    total=Sum('monto'),
    cantidad=Count('id')
)
```

---

## ⚠️ REGLAS IMPORTANTES

### ✅ SIEMPRE:
1. Separar Venta de Transacción
2. Calcular totales automáticamente
3. Validar saldo de crédito del cliente
4. Registrar todas las transacciones
5. Mantener histórico completo

### ❌ NUNCA:
1. Mezclar venta con pago
2. Modificar ventas cerradas
3. Eliminar transacciones
4. Permitir crédito sin límite
5. Olvidar actualizar inventario

---

## 🎯 PRÓXIMOS PASOS

1. Revisar modelos actuales
2. Crear migraciones necesarias
3. Actualizar lógica de ventas
4. Implementar pagos de crédito
5. Crear reportes avanzados

---

**Última actualización:** Marzo 2026  
**Versión:** 1.0  
**Sistema:** Lemon POS


---

## 7️⃣ MANEJO DE "CONSUMIDOR FINAL"

### Concepto

**Consumidor Final** en facturación significa:
- Cliente no identificado
- Venta anónima
- No se emitió factura con datos personales

### ✅ Implementación Profesional

En lugar de dejar `cliente = null`, los POS profesionales crean un **cliente fijo** en la base de datos:

```python
# Cliente por defecto en la base de datos
Cliente.objects.create(
    id=1,  # ID fijo
    nombre='Consumidor Final',
    identificacion='9999999999',  # Estándar Ecuador
    telefono=None,
    email=None,
    cupo=0,
    tasa_descuento=0,
    tasa_recargo=0,
    estado='activo',
    es_consumidor_final=True  # Flag especial
)
```

### Ventajas de este Enfoque

1. **Simplicidad:** Todas las ventas SIEMPRE tienen un cliente
2. **Consistencia:** No hay valores NULL en `venta.cliente_id`
3. **Reportes:** Más fácil agrupar y contar
4. **Facturación:** Datos estándar para SRI Ecuador

### Flujo en el POS

```python
# Al iniciar una venta
venta = Venta.objects.create(
    cliente_id=1,  # Consumidor Final por defecto
    usuario_creador=request.user,
    ...
)

# Si el cajero selecciona un cliente
venta.cliente_id = 25  # Juan Pérez
venta.save()

# Si no hace nada
# Se queda con cliente_id = 1 (Consumidor Final)
```

### Restricciones para Consumidor Final

```python
# Validación en el backend
if venta.cliente.es_consumidor_final:
    # NO permitir:
    if metodo_pago == 'credit':
        raise ValidationError('Consumidor Final no puede comprar a crédito')
    
    # Solo permitir:
    # - cash
    # - card
    # - transfer
```

### Datos para Facturación Electrónica (Ecuador)

Cuando es Consumidor Final:
```python
{
    'identificacion': '9999999999',
    'tipo_identificacion': '07',  # Consumidor Final
    'razon_social': 'CONSUMIDOR FINAL',
    'direccion': 'N/A',
    'telefono': 'N/A',
    'email': 'consumidorfinal@lemonpos.com'
}
```

### Método Helper en el Modelo

```python
class Cliente(models.Model):
    # ... campos ...
    
    @classmethod
    def get_consumidor_final(cls):
        """Obtiene o crea el cliente Consumidor Final"""
        cliente, created = cls.objects.get_or_create(
            identificacion='9999999999',
            defaults={
                'nombre': 'Consumidor Final',
                'cupo': 0,
                'tasa_descuento': 0,
                'tasa_recargo': 0,
                'estado': 'activo',
                'es_consumidor_final': True
            }
        )
        return cliente
    
    def puede_comprar_a_credito(self):
        """Verifica si el cliente puede comprar a crédito"""
        if self.es_consumidor_final:
            return False
        return self.cupo > 0 and self.estado == 'activo'
```

### UI en el POS

```html
<!-- Estado inicial -->
<div id="customer-display">
    Cliente: Consumidor Final
    <button onclick="cambiarCliente()">Cambiar</button>
</div>

<!-- Después de seleccionar cliente -->
<div id="customer-display">
    Cliente: Juan Pérez (0923456789)
    <button onclick="cambiarCliente()">Cambiar</button>
    <button onclick="quitarCliente()">Quitar</button>
</div>
```

### Comando de Inicialización

Crear comando Django para inicializar el sistema:

```bash
python manage.py inicializar_consumidor_final
```

Este comando:
1. Verifica si existe el cliente con ID 1
2. Si no existe, lo crea
3. Si existe, actualiza sus datos

---

## 🎯 CHECKLIST DE IMPLEMENTACIÓN

### Modelo Cliente
- [ ] Agregar campo `es_consumidor_final` (BooleanField)
- [ ] Crear método `get_consumidor_final()`
- [ ] Crear método `puede_comprar_a_credito()`

### Comando de Inicialización
- [ ] Crear `management/commands/inicializar_consumidor_final.py`
- [ ] Ejecutar en cada deploy
- [ ] Agregar a documentación de setup

### Validaciones
- [ ] Validar que Consumidor Final no pueda comprar a crédito
- [ ] Validar que Consumidor Final no tenga cupo
- [ ] Validar que no se pueda eliminar Consumidor Final

### UI
- [ ] Iniciar ventas con Consumidor Final seleccionado
- [ ] Botón "Cambiar" para seleccionar otro cliente
- [ ] Botón "Quitar" para volver a Consumidor Final

### Reportes
- [ ] Filtrar Consumidor Final en reportes de clientes
- [ ] Mostrar ventas a Consumidor Final separadas
- [ ] Estadísticas: % ventas con cliente vs sin cliente

---

**Nota:** Esta arquitectura es estándar en POS profesionales como Square, Toast, Lightspeed y sistemas locales ecuatorianos.
