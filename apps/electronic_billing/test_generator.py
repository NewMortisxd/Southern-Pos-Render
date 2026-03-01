"""
Script de prueba para el generador de XML de facturas electrónicas.
Ejecutar desde la raíz del proyecto: python -m apps.electronic_billing.test_generator
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'southern_food_pos.settings')
django.setup()

from apps.ventas.models import Venta
from apps.electronic_billing.services.xml_generator import InvoiceXMLGenerator
from apps.electronic_billing.services.xsd_validator import validate_invoice_xml


def test_xml_generation():
    """Prueba la generación y validación de XML"""
    print("=" * 80)
    print("PRUEBA DE GENERACIÓN Y VALIDACIÓN DE XML")
    print("=" * 80)
    
    # Obtener la última venta
    try:
        sale = Venta.objects.select_related('cliente').prefetch_related('detalleventa_set__producto').first()
        
        if not sale:
            print("❌ No hay ventas en la base de datos.")
            print("   Crea una venta de prueba primero.")
            return
        
        print(f"\n✅ Venta encontrada: #{sale.id}")
        print(f"   Cliente: {sale.cliente.nombre if sale.cliente else 'Consumidor Final'}")
        print(f"   Total: ${sale.total}")
        print(f"   Fecha: {sale.fecha_hora}")
        
        # Generar XML
        print("\n🔄 Generando XML...")
        generator = InvoiceXMLGenerator(sale)
        xml_bytes = generator.generate()
        
        print(f"✅ XML generado ({len(xml_bytes)} bytes)")
        
        # Validar XML
        print("\n🔄 Validando contra XSD del SRI...")
        is_valid, errors = validate_invoice_xml(xml_bytes)
        
        if is_valid:
            print("✅ XML VÁLIDO - Cumple con el XSD del SRI")
        else:
            print(f"❌ XML INVÁLIDO - {len(errors)} errores encontrados:")
            for i, error in enumerate(errors, 1):
                print(f"\n   Error {i}:")
                print(f"   Línea: {error['linea']}, Columna: {error['columna']}")
                print(f"   Mensaje: {error['mensaje']}")
        
        # Mostrar XML
        print("\n" + "=" * 80)
        print("XML GENERADO:")
        print("=" * 80)
        print(xml_bytes.decode('utf-8'))
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_xml_generation()
