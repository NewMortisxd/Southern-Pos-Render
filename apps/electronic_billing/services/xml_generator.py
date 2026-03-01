"""
Generador de XML de factura electrónica según especificaciones del SRI Ecuador
Versión: 1.1.0
"""
from lxml import etree
from datetime import datetime
from decimal import Decimal


class InvoiceXMLGenerator:
    """
    Genera XML de factura electrónica desde un objeto Venta de Django.
    Respeta el orden exacto requerido por el XSD del SRI versión 1.1.0
    """
    
    def __init__(self, sale):
        """
        Args:
            sale: Objeto apps.ventas.models.Venta
        """
        self.sale = sale
        
        # Get IVA rate from business settings
        try:
            from apps.usuarios.models import Business
            business = Business.objects.get(user=sale.usuario_creador)
            self.tax_rate = business.iva_porcentaje / Decimal('100')  # Convert percentage to decimal
            self.tax_percentage = int(business.iva_porcentaje)  # For display (e.g., 12, 15)
        except:
            # Default to 12% IVA for Ecuador
            self.tax_rate = Decimal("0.12")
            self.tax_percentage = 12
        
        # Calcular totales desglosados (precios incluyen IVA)
        self._calculate_totals()
        
    def _calculate_totals(self):
        """
        Calcula los totales desglosados correctamente.
        Los precios en el sistema incluyen IVA, debemos desglosarlos.
        
        IMPORTANTE: Para evitar errores de redondeo acumulativo:
        1. Calculamos base de cada item desde su subtotal (no precio_unitario * cantidad)
        2. Redondeamos cada línea a 2 decimales
        3. Sumamos las líneas redondeadas (no los valores exactos)
        4. El totalSinImpuestos DEBE ser igual a la suma de precioTotalSinImpuesto
        
        Ejemplo:
        - Item 1: $18.99 → base = 16.96 (redondeado)
        - Item 2: $15.99 → base = 14.28 (redondeado)
        - totalSinImpuestos = 16.96 + 14.28 = 31.24 (suma de líneas)
        - NO recalcular desde valores exactos
        """
        items = self.sale.detalleventa_set.all()
        
        base_total = Decimal("0")
        
        # Lista para almacenar las bases redondeadas de cada línea
        self.item_bases = []
        
        for item in items:
            # El subtotal del item incluye IVA
            # Desglosar: base = subtotal / 1.12
            base_item_exact = item.subtotal / (Decimal("1") + self.tax_rate)
            
            # Redondear la base de esta línea
            base_item_rounded = base_item_exact.quantize(Decimal("0.01"))
            
            # Guardar para usar en _build_detalle_item
            self.item_bases.append({
                'item_id': item.id,
                'base': base_item_rounded,
                'iva': item.subtotal - base_item_rounded
            })
            
            # Acumular la base REDONDEADA (no exacta)
            base_total += base_item_rounded
        
        # totalSinImpuestos = suma de las líneas redondeadas
        self.base_imponible_total = base_total
        
        # IVA total = total de venta - base total
        self.iva_total = self.sale.total - self.base_imponible_total
        
        # Verificación de consistencia
        # base + iva debe ser igual al total de la venta (siempre se cumple por construcción)
        total_calculado = self.base_imponible_total + self.iva_total
        
        # Ajuste de seguridad por si hay diferencia microscópica
        diferencia = self.sale.total - total_calculado
        if abs(diferencia) > Decimal("0.001"):
            # Esto no debería pasar, pero por seguridad
            self.iva_total += diferencia
    
    def generate(self) -> bytes:
        """
        Genera el XML completo de la factura.
        
        Returns:
            bytes: XML en formato UTF-8
        """
        # Namespace del SRI
        nsmap = {None: "http://www.sri.gob.ec/schemas/factura"}
        
        # Elemento raíz
        root = etree.Element("factura", nsmap=nsmap, id="comprobante", version="1.1.0")
        
        # 1. infoTributaria
        info_tributaria = self._build_info_tributaria()
        root.append(info_tributaria)
        
        # 2. infoFactura
        info_factura = self._build_info_factura()
        root.append(info_factura)
        
        # 3. detalles
        detalles = self._build_detalles()
        root.append(detalles)
        
        # 4. infoAdicional (opcional)
        info_adicional = self._build_info_adicional()
        if info_adicional is not None:
            root.append(info_adicional)
        
        # Convertir a bytes con formato
        xml_bytes = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
        
        return xml_bytes
    
    def _build_info_tributaria(self):
        """Construye el nodo infoTributaria"""
        info = etree.Element("infoTributaria")
        
        # Datos de prueba - en producción vendrían de la configuración del negocio
        self._add_element(info, "ambiente", "1")  # 1=Pruebas, 2=Producción
        self._add_element(info, "tipoEmision", "1")  # 1=Normal
        self._add_element(info, "razonSocial", "EMPRESA DE PRUEBA S.A.")
        self._add_element(info, "nombreComercial", "EMPRESA PRUEBA")
        self._add_element(info, "ruc", "1234567890001")
        self._add_element(info, "claveAcceso", self._generate_access_key())
        self._add_element(info, "codDoc", "01")  # 01=Factura
        self._add_element(info, "estab", "001")
        self._add_element(info, "ptoEmi", "001")
        self._add_element(info, "secuencial", str(self.sale.id).zfill(9))
        self._add_element(info, "dirMatriz", "AV. PRINCIPAL 123 Y SECUNDARIA")
        
        return info
    
    def _build_info_factura(self):
        """Construye el nodo infoFactura - ORDEN CRÍTICO"""
        info = etree.Element("infoFactura")
        
        # Fecha en formato dd/mm/yyyy
        fecha = self.sale.fecha_hora.strftime("%d/%m/%Y")
        self._add_element(info, "fechaEmision", fecha)
        
        self._add_element(info, "dirEstablecimiento", "AV. PRINCIPAL 123 Y SECUNDARIA")
        
        # Obligado a llevar contabilidad
        self._add_element(info, "obligadoContabilidad", "SI")
        
        # Datos del comprador
        cliente = self.sale.cliente
        if cliente:
            # Tipo de identificación: 04=RUC, 05=Cédula, 06=Pasaporte, 07=Consumidor Final
            tipo_id = self._get_identification_type(cliente.identificacion)
            self._add_element(info, "tipoIdentificacionComprador", tipo_id)
            self._add_element(info, "razonSocialComprador", cliente.nombre[:300])
            self._add_element(info, "identificacionComprador", cliente.identificacion)
            
            # Dirección del comprador (opcional pero incluido)
            if cliente.direccion:
                self._add_element(info, "direccionComprador", cliente.direccion[:300])
        else:
            # Consumidor final
            self._add_element(info, "tipoIdentificacionComprador", "07")
            self._add_element(info, "razonSocialComprador", "CONSUMIDOR FINAL")
            self._add_element(info, "identificacionComprador", "9999999999999")
        
        # Totales (usar valores calculados correctamente)
        self._add_element(info, "totalSinImpuestos", self._format_decimal(self.base_imponible_total))
        self._add_element(info, "totalDescuento", "0.00")
        
        # totalConImpuestos
        total_impuestos = self._build_total_impuestos()
        info.append(total_impuestos)
        
        self._add_element(info, "propina", "0.00")
        self._add_element(info, "importeTotal", self._format_decimal(self.sale.total))
        self._add_element(info, "moneda", "DOLAR")
        
        # Pagos
        pagos = self._build_pagos()
        info.append(pagos)
        
        return info
    
    def _build_total_impuestos(self):
        """Construye el nodo totalConImpuestos"""
        total_impuestos = etree.Element("totalConImpuestos")
        
        # Total de IVA (usar valores calculados correctamente)
        total_impuesto = etree.SubElement(total_impuestos, "totalImpuesto")
        self._add_element(total_impuesto, "codigo", "2")  # 2=IVA
        
        # Código de porcentaje según la tasa
        # 0=0%, 2=12%, 3=14%, 4=15% (según tabla del SRI)
        codigo_porcentaje = self._get_codigo_porcentaje()
        self._add_element(total_impuesto, "codigoPorcentaje", codigo_porcentaje)
        
        self._add_element(total_impuesto, "baseImponible", self._format_decimal(self.base_imponible_total))
        self._add_element(total_impuesto, "valor", self._format_decimal(self.iva_total))
        
        return total_impuestos
    
    def _build_pagos(self):
        """Construye el nodo pagos"""
        pagos = etree.Element("pagos")
        
        pago = etree.SubElement(pagos, "pago")
        
        # Forma de pago: 01=Sin utilizacion del sistema financiero
        # 16=Tarjeta de débito, 19=Tarjeta de crédito, 20=Otros
        forma_pago = self._get_payment_method_code(self.sale.metodo_pago)
        self._add_element(pago, "formaPago", forma_pago)
        self._add_element(pago, "total", self._format_decimal(self.sale.total))
        
        return pagos
    
    def _build_detalles(self):
        """Construye el nodo detalles con todos los items"""
        detalles = etree.Element("detalles")
        
        items = self.sale.detalleventa_set.all()
        
        for item in items:
            detalle = self._build_detalle_item(item)
            detalles.append(detalle)
        
        return detalles
    
    def _build_detalle_item(self, item):
        """Construye un nodo detalle individual - ORDEN CRÍTICO"""
        detalle = etree.Element("detalle")
        
        # Código principal del producto
        producto = item.producto
        codigo = producto.codigo if hasattr(producto, 'codigo') and producto.codigo else str(producto.id)
        self._add_element(detalle, "codigoPrincipal", codigo[:25])
        
        # Descripción
        self._add_element(detalle, "descripcion", producto.nombre[:300])
        
        # Cantidad
        self._add_element(detalle, "cantidad", str(item.cantidad))
        
        # Buscar los valores pre-calculados para este item
        item_data = next((x for x in self.item_bases if x['item_id'] == item.id), None)
        
        if item_data:
            base_imponible_item = item_data['base']
            iva_item = item_data['iva']
        else:
            # Fallback (no debería pasar)
            base_imponible_item = (item.subtotal / (Decimal("1") + self.tax_rate)).quantize(Decimal("0.01"))
            iva_item = item.subtotal - base_imponible_item
        
        # Precio unitario sin IVA = base / cantidad
        precio_unit_sin_iva = base_imponible_item / Decimal(str(item.cantidad))
        self._add_element(detalle, "precioUnitario", self._format_decimal(precio_unit_sin_iva))
        
        # Descuento
        self._add_element(detalle, "descuento", "0.00")
        
        # Base imponible (precioTotalSinImpuesto) - usar valor redondeado
        self._add_element(detalle, "precioTotalSinImpuesto", self._format_decimal(base_imponible_item))
        
        # Impuestos del item
        impuestos = etree.SubElement(detalle, "impuestos")
        impuesto = etree.SubElement(impuestos, "impuesto")
        
        self._add_element(impuesto, "codigo", "2")  # 2=IVA
        
        # Código de porcentaje según la tasa configurada
        codigo_porcentaje = self._get_codigo_porcentaje()
        self._add_element(impuesto, "codigoPorcentaje", codigo_porcentaje)
        self._add_element(impuesto, "tarifa", str(self.tax_percentage))
        
        self._add_element(impuesto, "baseImponible", self._format_decimal(base_imponible_item))
        
        # IVA del item (ya calculado)
        self._add_element(impuesto, "valor", self._format_decimal(iva_item))
        
        return detalle
    
    def _build_info_adicional(self):
        """Construye el nodo infoAdicional (opcional)"""
        info_adicional = etree.Element("infoAdicional")
        
        # Email del cliente si existe
        if self.sale.cliente and self.sale.cliente.email:
            campo = etree.SubElement(info_adicional, "campoAdicional", nombre="Email")
            campo.text = self.sale.cliente.email
        
        # Teléfono del cliente si existe
        if self.sale.cliente and self.sale.cliente.telefono:
            campo = etree.SubElement(info_adicional, "campoAdicional", nombre="Teléfono")
            campo.text = self.sale.cliente.telefono
        
        # Solo retornar si tiene campos
        if len(info_adicional) > 0:
            return info_adicional
        return None
    
    # Métodos auxiliares
    
    def _add_element(self, parent, tag, text):
        """Agrega un elemento hijo con texto"""
        elem = etree.SubElement(parent, tag)
        elem.text = str(text) if text is not None else ""
        return elem
    
    def _format_decimal(self, value):
        """Formatea un decimal a string con 2 decimales"""
        if value is None:
            return "0.00"
        return f"{float(value):.2f}"
    
    def _get_identification_type(self, identification):
        """Determina el tipo de identificación según la longitud"""
        if not identification:
            return "07"  # Consumidor final
        
        id_clean = identification.strip()
        length = len(id_clean)
        
        if length == 13:
            return "04"  # RUC
        elif length == 10:
            return "05"  # Cédula
        elif length > 0:
            return "06"  # Pasaporte
        else:
            return "07"  # Consumidor final
    
    def _get_payment_method_code(self, metodo_pago):
        """Convierte el método de pago interno al código del SRI"""
        mapping = {
            'cash': '01',  # Sin utilización del sistema financiero
            'card': '19',  # Tarjeta de crédito
            'transfer': '20',  # Otros con utilización del sistema financiero
        }
        return mapping.get(metodo_pago, '20')
    
    def _get_codigo_porcentaje(self):
        """
        Mapea el porcentaje de IVA al código del SRI Ecuador.
        
        Códigos oficiales según SRI Ecuador (actualizados 2024):
        0 = 0%
        2 = 12% (histórico, antes de abril 2024)
        3 = 14% (histórico, incremento temporal post-terremoto 2016)
        4 = 15% (VIGENTE desde abril 2024)
        6 = No objeto de impuesto
        7 = Exento de IVA
        8 = IVA diferenciado
        
        IMPORTANTE: Desde abril 2024, la tarifa general de IVA en Ecuador es 15%.
        El sistema soporta tarifas históricas para documentos antiguos.
        """
        # Redondear el porcentaje para comparación
        tax_pct = round(float(self.tax_percentage))
        
        if tax_pct == 0:
            return "0"
        elif tax_pct == 12:
            return "2"  # Histórico
        elif tax_pct == 14:
            return "3"  # Histórico
        elif tax_pct == 15:
            return "4"  # VIGENTE
        else:
            # El SRI no acepta otros porcentajes
            raise ValueError(
                f"Porcentaje de IVA {tax_pct}% no es válido para el SRI Ecuador. "
                f"Valores permitidos: 0%, 12% (histórico), 14% (histórico), 15% (vigente). "
                f"Por favor, actualiza la configuración del negocio (Business.iva_porcentaje)."
            )
    
    def _generate_access_key(self):
        """
        Genera una clave de acceso de 49 dígitos según el algoritmo del SRI.
        NOTA: Esta es una versión simplificada para pruebas.
        En producción debe implementarse el algoritmo completo con módulo 11.
        """
        fecha = self.sale.fecha_hora.strftime("%d%m%Y")  # 8 dígitos
        tipo_comprobante = "01"  # 2 dígitos - Factura
        ruc = "1234567890001"  # 13 dígitos
        ambiente = "1"  # 1 dígito - Pruebas
        serie = "001001"  # 6 dígitos (estab + ptoEmi)
        secuencial = str(self.sale.id).zfill(9)[:9]  # 9 dígitos exactos
        codigo_numerico = "12345678"  # 8 dígitos - Aleatorio en producción
        tipo_emision = "1"  # 1 dígito - Normal
        
        # Concatenar sin dígito verificador (48 dígitos)
        clave_parcial = fecha + tipo_comprobante + ruc + ambiente + serie + secuencial + codigo_numerico + tipo_emision
        
        # Verificar que tengamos exactamente 48 dígitos antes del verificador
        if len(clave_parcial) != 48:
            raise ValueError(f"Clave parcial debe tener 48 dígitos, tiene {len(clave_parcial)}: {clave_parcial}")
        
        # Calcular dígito verificador (módulo 11)
        digito = self._calcular_digito_verificador(clave_parcial)
        
        clave_completa = clave_parcial + str(digito)
        
        # Verificar que la clave completa tenga 49 dígitos
        if len(clave_completa) != 49:
            raise ValueError(f"Clave de acceso debe tener 49 dígitos, tiene {len(clave_completa)}: {clave_completa}")
        
        return clave_completa
    
    def _calcular_digito_verificador(self, clave):
        """
        Calcula el dígito verificador usando módulo 11.
        Retorna un dígito del 0 al 9.
        """
        factor = 2
        suma = 0
        
        for i in range(len(clave) - 1, -1, -1):
            suma += int(clave[i]) * factor
            factor = factor + 1 if factor < 7 else 2
        
        residuo = suma % 11
        digito = 11 - residuo
        
        # Si el dígito es 11, usar 0
        # Si el dígito es 10, usar 1 (según especificación del SRI)
        if digito == 11:
            return 0
        elif digito == 10:
            return 1
        else:
            return digito
