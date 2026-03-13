"""
Servicios para facturación electrónica SRI Ecuador
"""
from django.db import transaction
from django.db.models import F
from decimal import Decimal
import random
from datetime import datetime


def generar_clave_acceso(venta, business):
    """
    Genera clave de acceso de 49 dígitos según especificaciones SRI Ecuador.
    
    Formato: DDMMYYYYTTCCCCCCCCCRRRRRRRRRRCDE
    
    Donde:
    - DD: Día (2 dígitos)
    - MM: Mes (2 dígitos)
    - YYYY: Año (4 dígitos)
    - TT: Tipo de comprobante (2 dígitos) - 01 = Factura
    - CCCCCCCCC: RUC (13 dígitos)
    - RRR: Ambiente (1 dígito) + Tipo emisión (1 dígito) + Serie (6 dígitos)
    - RRRRRRRRR: Secuencial (9 dígitos)
    - C: Código numérico (8 dígitos)
    - D: Tipo emisión (1 dígito)
    - E: Dígito verificador (1 dígito)
    
    Args:
        venta: Instancia de Venta
        business: Instancia de Business
    
    Returns:
        str: Clave de acceso de 49 dígitos
    """
    # Fecha de emisión
    fecha = venta.fecha_hora.strftime('%d%m%Y')
    
    # Tipo de comprobante (01 = Factura)
    tipo_comprobante = '01'
    
    # RUC (13 dígitos, rellenar con ceros si es necesario)
    ruc = str(business.ruc_negocio).zfill(13)
    
    # Ambiente (1 = Pruebas, 2 = Producción)
    ambiente = business.ambiente_sri
    
    # Serie (establecimiento + punto emisión)
    serie = f"{venta.establecimiento_codigo}{venta.punto_emision_codigo}"
    
    # Secuencial (9 dígitos)
    secuencial = f"{venta.secuencial:09d}"
    
    # Código numérico (8 dígitos aleatorios)
    codigo_numerico = f"{random.randint(10000000, 99999999)}"
    
    # Tipo de emisión (1 = Normal, 2 = Indisponibilidad)
    tipo_emision = business.tipo_emision
    
    # Construir clave sin dígito verificador
    clave_sin_digito = (
        fecha + tipo_comprobante + ruc + ambiente + 
        serie + secuencial + codigo_numerico + tipo_emision
    )
    
    # Calcular dígito verificador
    digito_verificador = calcular_digito_verificador_modulo11(clave_sin_digito)
    
    # Clave completa
    clave_acceso = clave_sin_digito + str(digito_verificador)
    
    return clave_acceso


def calcular_digito_verificador_modulo11(clave):
    """
    Calcula el dígito verificador según algoritmo módulo 11 del SRI.
    
    Args:
        clave (str): Cadena numérica de 48 dígitos
    
    Returns:
        int: Dígito verificador (0-9)
    """
    factor = 7
    suma = 0
    
    for digito in clave:
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    
    residuo = suma % 11
    digito = 11 - residuo if residuo != 0 else 0
    
    return 0 if digito == 11 else digito


@transaction.atomic
def crear_venta_con_factura(usuario, punto_emision, datos_venta, items):
    """
    Crea una venta con número de factura electrónica.
    
    🎯 FLUJO CORRECTO:
    1. Obtener punto de emisión con lock
    2. Generar número de factura
    3. Crear venta con todos los datos
    4. Generar clave de acceso
    5. Incrementar secuencial
    6. Crear detalles de venta
    
    ⚠️ IMPORTANTE:
    - El secuencial se incrementa AL MOMENTO de emitir, no cuando SRI autoriza
    - Si SRI rechaza, ese número queda usado (regla tributaria)
    - Usar transacción atómica para garantizar consistencia
    
    Args:
        usuario: Usuario que crea la venta
        punto_emision: Instancia de PuntoEmision
        datos_venta: Dict con datos de la venta (cliente, total, metodo_pago, etc)
        items: List de items de la venta
    
    Returns:
        Venta: Instancia de venta creada
    """
    from apps.ventas.models import Venta, DetalleVenta, PuntoEmision
    from apps.usuarios.models import Business
    
    # 1. Obtener punto de emisión con lock para prevenir race conditions
    punto = PuntoEmision.objects.select_for_update().get(pk=punto_emision.pk)
    
    # 2. Generar número de factura
    establecimiento, codigo_punto, secuencial, numero_factura = punto.generar_numero_factura()
    
    # 3. Obtener business para clave de acceso
    business = Business.objects.get(user=usuario)
    
    # 4. Crear venta
    venta = Venta.objects.create(
        usuario_creador=usuario,
        punto_emision=punto,
        establecimiento_codigo=establecimiento,
        punto_emision_codigo=codigo_punto,
        secuencial=secuencial,
        numero_factura=numero_factura,
        estado_sri='PENDIENTE',
        **datos_venta
    )
    
    # 5. Generar clave de acceso (debe ser determinística)
    clave_acceso = generar_clave_acceso(venta, business)
    venta.clave_acceso = clave_acceso
    venta.save(update_fields=['clave_acceso'])
    
    # 6. Crear detalles de venta
    for item in items:
        DetalleVenta.objects.create(
            venta=venta,
            **item
        )
    
    return venta


def validar_formato_codigo(codigo, nombre_campo='código'):
    """
    Valida que un código sea exactamente 3 dígitos numéricos.
    
    Args:
        codigo (str): Código a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if not codigo:
        return False, f"El {nombre_campo} es requerido"
    
    if len(codigo) != 3:
        return False, f"El {nombre_campo} debe tener exactamente 3 dígitos"
    
    if not codigo.isdigit():
        return False, f"El {nombre_campo} debe contener solo dígitos numéricos"
    
    return True, ""


def formatear_codigo(numero):
    """
    Formatea un número a código de 3 dígitos.
    
    Args:
        numero (int): Número a formatear
    
    Returns:
        str: Código de 3 dígitos (ej: 1 -> '001')
    """
    return f"{int(numero):03d}"



# ============================================
# SERVICIOS PARA ÓRDENES (MODO RESTAURANTE)
# ============================================

class OrderService:
    """
    Servicio para manejar órdenes en modo restaurante.
    Placeholder para mantener compatibilidad.
    """
    
    @staticmethod
    def create_order(business, items, table_number=None):
        """Crea una nueva orden"""
        from apps.ventas.models import Order
        # Implementación básica
        pass
    
    @staticmethod
    def update_order_status(order_id, new_status):
        """Actualiza el estado de una orden"""
        from apps.ventas.models import Order
        # Implementación básica
        pass
