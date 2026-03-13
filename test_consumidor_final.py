"""
Script de prueba para verificar el flujo de Consumidor Final
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'southern_food_pos.settings')
django.setup()

from apps.clients.models import Cliente
from apps.ventas.models import Venta
from apps.usuarios.models import Usuario
from decimal import Decimal

def test_consumidor_final():
    """
    Prueba el flujo completo de Consumidor Final
    """
    print("=" * 60)
    print("🧪 TEST: FLUJO DE CONSUMIDOR FINAL")
    print("=" * 60)
    
    # 1. Obtener usuario de prueba
    usuario = Usuario.objects.first()
    if not usuario:
        print("❌ No hay usuarios en el sistema")
        return
    
    print(f"\n✓ Usuario: {usuario.username}")
    
    # 2. Obtener o crear Consumidor Final
    consumidor_final = Cliente.get_consumidor_final(usuario)
    print(f"\n✓ Consumidor Final obtenido:")
    print(f"   - ID: {consumidor_final.id}")
    print(f"   - Nombre: {consumidor_final.nombre}")
    print(f"   - Identificación: {consumidor_final.identificacion}")
    print(f"   - Es Consumidor Final: {consumidor_final.es_consumidor_final()}")
    
    # 3. Verificar que NO puede comprar a crédito
    puede_credito = consumidor_final.puede_comprar_a_credito()
    print(f"\n✓ Puede comprar a crédito: {puede_credito}")
    if not puede_credito:
        print("   ✅ CORRECTO: Consumidor Final NO puede comprar a crédito")
    else:
        print("   ❌ ERROR: Consumidor Final NO debería poder comprar a crédito")
    
    # 4. Verificar descuentos y recargos
    print(f"\n✓ Descuento: {consumidor_final.tasa_descuento}%")
    print(f"✓ Recargo: {consumidor_final.tasa_recargo}%")
    print(f"✓ Cupo: ${consumidor_final.cupo}")
    print(f"✓ Crédito días: {consumidor_final.credito}")
    
    if (consumidor_final.tasa_descuento == 0 and 
        consumidor_final.tasa_recargo == 0 and 
        consumidor_final.cupo == 0 and 
        consumidor_final.credito == 0):
        print("   ✅ CORRECTO: Consumidor Final sin descuentos, recargos ni crédito")
    else:
        print("   ❌ ERROR: Consumidor Final debería tener todo en 0")
    
    # 5. Simular creación de venta
    print("\n" + "=" * 60)
    print("🧪 SIMULANDO CREACIÓN DE VENTA")
    print("=" * 60)
    
    try:
        venta = Venta(
            usuario_creador=usuario,
            cliente=consumidor_final,
            subtotal=Decimal('10.87'),
            descuento_total=Decimal('0.00'),
            recargo_total=Decimal('0.00'),
            iva=Decimal('1.63'),
            total=Decimal('12.50'),
            metodo_pago='cash',
            monto_recibido=Decimal('20.00'),
            cambio=Decimal('7.50'),
            estado_pago='pagado'
        )
        
        print(f"\n✓ Venta creada (sin guardar):")
        print(f"   - Cliente: {venta.cliente.nombre}")
        print(f"   - Subtotal: ${venta.subtotal}")
        print(f"   - Descuento: ${venta.descuento_total}")
        print(f"   - Recargo: ${venta.recargo_total}")
        print(f"   - IVA: ${venta.iva}")
        print(f"   - Total: ${venta.total}")
        print(f"   - Método pago: {venta.metodo_pago}")
        print(f"   - Estado pago: {venta.estado_pago}")
        
        # Verificar que no puede pagar a crédito
        puede_pagar_credito = venta.puede_pagar_credito()
        print(f"\n✓ Venta puede pagar a crédito: {puede_pagar_credito}")
        if not puede_pagar_credito:
            print("   ✅ CORRECTO: Venta con Consumidor Final NO puede ser a crédito")
        else:
            print("   ❌ ERROR: Venta con Consumidor Final NO debería poder ser a crédito")
        
        # 6. Intentar crear venta a crédito (debe fallar)
        print("\n" + "=" * 60)
        print("🧪 INTENTANDO CREAR VENTA A CRÉDITO (debe fallar)")
        print("=" * 60)
        
        venta_credito = Venta(
            usuario_creador=usuario,
            cliente=consumidor_final,
            subtotal=Decimal('10.87'),
            iva=Decimal('1.63'),
            total=Decimal('12.50'),
            metodo_pago='credit',
            estado_pago='pendiente',
            saldo_pendiente=Decimal('12.50')
        )
        
        try:
            venta_credito.save()
            print("   ❌ ERROR: Se permitió crear venta a crédito con Consumidor Final")
        except ValueError as e:
            print(f"   ✅ CORRECTO: Venta a crédito bloqueada - {e}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETADO")
    print("=" * 60)

if __name__ == '__main__':
    test_consumidor_final()
