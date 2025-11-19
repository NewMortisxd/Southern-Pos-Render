from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.productos.models import Producto, Categoria
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, FloatField
from django.db.models.functions import Coalesce
import csv
from django.http import HttpResponse
from datetime import datetime
from django.core.paginator import Paginator
from apps.transacciones.models import Transaccion
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.contrib import messages
import io  # Add this import for StringIO
from django.shortcuts import redirect  # Also add this for the redirect function

@login_required
def reportes_view(request):
    """Vista principal del panel de reportes"""
    return render(request, 'reportes/reportes.html')

# Reportes Financieros y Fiscales
@login_required
def ventas_report(request):
    """Reporte de ventas diarias, semanales, mensuales y anuales"""
    return render(request, 'reportes/ventas.html')

@login_required
def iva_report(request):
    """Reporte de IVA"""
    return render(request, 'reportes/iva.html')

@login_required
def facturas_report(request):
    """Reporte de facturas y comprobantes"""
    return render(request, 'reportes/facturas.html')

# Reportes Operativos
@login_required
def inventario_report(request):
    """Reporte de inventario"""
    # Obtener solo los productos del usuario actual ordenados por stock
    productos = Producto.objects.filter(usuario_creador=request.user).order_by('stock')
    
    # Productos con stock bajo (menos de 10 unidades)
    productos_stock_bajo = productos.filter(stock__lt=10)
    
    # Productos agotados
    productos_agotados = productos.filter(stock=0)
    
    # Productos por categoría - Solo categorías con productos del usuario
    categorias = Categoria.objects.filter(producto__usuario_creador=request.user).distinct().annotate(
        total_productos=Count('producto', filter=Q(producto__usuario_creador=request.user))
    )
    
    # Calculate valor_inventario separately for each category
    for categoria in categorias:
        productos_categoria = Producto.objects.filter(categoria=categoria, usuario_creador=request.user)
        valor_inventario = sum(p.precio * p.stock for p in productos_categoria)
        categoria.valor_inventario = valor_inventario
    
    # Valor total del inventario - Calculate directly
    valor_total = sum(p.precio * p.stock for p in productos)
    
    context = {
        'productos': productos,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_agotados': productos_agotados,
        'categorias': categorias,
        'valor_total': valor_total,
        'total_productos': productos.count(),
        'total_categorias': categorias.count(),
    }
    
    return render(request, 'reportes/inventario.html', context)

@login_required
def analisis_ventas_report(request):
    """Análisis de ventas"""
    return render(request, 'reportes/analisis_ventas.html')

@login_required
def clientes_report(request):
    """Reporte de clientes"""
    return render(request, 'reportes/clientes.html')

# Reportes para el SRI
@login_required
def ats_report(request):
    """Anexo Transaccional Simplificado (ATS)"""
    return render(request, 'reportes/ats.html')

@login_required
def iva_declaracion_report(request):
    """Declaración del IVA (Formulario 104)"""
    return render(request, 'reportes/iva_declaracion.html')

@login_required
def renta_report(request):
    """Declaración del Impuesto a la Renta"""
    return render(request, 'reportes/renta.html')

# Reportes Rápidos
@login_required
def ventas_diarias_report(request):
    """Reporte de ventas del día"""
    return render(request, 'reportes/ventas_diarias.html')

@login_required
def productos_top_report(request):
    """Reporte de productos más vendidos"""
    return render(request, 'reportes/productos_top.html')

@login_required
def stock_bajo_report(request):
    """Reporte de productos con stock bajo"""
    return render(request, 'reportes/stock_bajo.html')

@login_required
def generar_xml(request):
    """Generación de archivos XML para el SRI"""
    return render(request, 'reportes/generar_xml.html')

# Add this function to your views.py
def exportar_ventas(request):
    """
    Export sales data to CSV based on filter parameters
    """
    # Get filter parameters
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    tipo_documento = request.GET.get('tipo_documento', 'todos')
    
    # Convert string dates to datetime objects if provided
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    else:
        fecha_desde = datetime.now().date().replace(day=1)  # First day of current month
        
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    else:
        fecha_hasta = datetime.now().date()
    
    # Query your database for facturas based on filters
    # This is a placeholder - adjust according to your models
    facturas = Factura.objects.filter(fecha__range=[fecha_desde, fecha_hasta])
    
    if tipo_documento != 'todos':
        facturas = facturas.filter(tipo=tipo_documento)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ventas_{fecha_desde}_a_{fecha_hasta}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow(['Número', 'Fecha', 'Cliente', 'Subtotal', 'IVA', 'Total', 'Estado'])
    
    # Add data rows
    for factura in facturas:
        writer.writerow([
            factura.numero,
            factura.fecha.strftime('%d/%m/%Y'),
            factura.cliente.nombre,
            factura.subtotal,
            factura.iva,
            factura.total,
            factura.estado
        ])
    
    return response


# Add these imports at the top of the file if they don't exist already
from django.shortcuts import render
from django.core.paginator import Paginator
from apps.transacciones.models import Transaccion
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone
import json

# Add or update the ventas view function
def ventas(request):
    # Get filter parameters
    fecha_desde = request.GET.get('fecha_desde', None)
    fecha_hasta = request.GET.get('fecha_hasta', None)
    tipo_documento = request.GET.get('tipo_documento', 'todos')
    
    # Set default date range if not provided (last 30 days)
    if not fecha_desde:
        fecha_desde = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_hasta:
        fecha_hasta = timezone.now().strftime('%Y-%m-%d')
    
    # Convert string dates to datetime objects
    fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
    fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
    fecha_hasta_dt = datetime.combine(fecha_hasta_dt.date(), datetime.max.time())  # Set to end of day
    
    # Query transactions based on filters
    transacciones = Transaccion.objects.filter(
        fecha__gte=fecha_desde_dt,
        fecha__lte=fecha_hasta_dt,
        procesado_pago=True,
        usuario_creador=request.user
    ).order_by('-fecha')
    
    # Apply document type filter if specified
    if tipo_documento != 'todos':
        # This is a simplified implementation - adjust based on your actual data model
        if tipo_documento == 'factura':
            # Filter for invoices
            transacciones = transacciones.filter(venta__tipo_documento='factura')
        elif tipo_documento == 'nota_venta':
            # Filter for sales notes
            transacciones = transacciones.filter(venta__tipo_documento='nota_venta')
        elif tipo_documento == 'ticket':
            # Filter for tickets
            transacciones = transacciones.filter(venta__tipo_documento='ticket')
    
    # Calculate summary statistics
    total_ventas = transacciones.aggregate(total=Sum('monto'))['total'] or 0
    
    # Calculate IVA correctly - moved after transacciones is defined
    total_iva = 0
    for transaccion in transacciones:
        # Calculate IVA as 15% of the subtotal (or total/1.15)
        total = float(transaccion.monto)
        subtotal = total / 1.15
        iva = total - subtotal
        total_iva += iva
    
    total_facturas = transacciones.count()
    
    # Calculate percentage change compared to previous period
    previous_start = fecha_desde_dt - (fecha_hasta_dt - fecha_desde_dt)
    previous_end = fecha_desde_dt - timedelta(days=1)
    
    previous_ventas = Transaccion.objects.filter(
        fecha__gte=previous_start,
        fecha__lte=previous_end,
        procesado_pago=True,
        usuario_creador=request.user
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    if previous_ventas > 0:
        porcentaje_cambio = ((total_ventas - previous_ventas) / previous_ventas) * 100
    else:
        porcentaje_cambio = 100 if total_ventas > 0 else 0
    
    # Prepare data for chart
    # Group transactions by date and sum amounts
    ventas_por_dia = {}
    for t in transacciones:
        fecha_str = t.fecha.strftime('%Y-%m-%d')
        if fecha_str in ventas_por_dia:
            ventas_por_dia[fecha_str] += float(t.monto)
        else:
            ventas_por_dia[fecha_str] = float(t.monto)
    
    # Sort by date and prepare for chart
    sorted_dates = sorted(ventas_por_dia.keys())
    ventas_chart_data = {
        'labels': [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m') for d in sorted_dates],
        'values': [ventas_por_dia[d] for d in sorted_dates]
    }
    
    # Additional statistics for SRI (tax authority)
    total_ventas_gravadas = total_ventas
    # Adjust this calculation based on your actual data model if you have tax-exempt sales
    
    proxima_declaracion = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) + timedelta(days=9)
    retenciones_recibidas = 0  # You would calculate this from your data
    retenciones_efectuadas = 0  # You would calculate this from your data
    estado_ats = 'pendiente'  # This would be determined by your business logic
    
    # Pagination
    paginator = Paginator(transacciones, 10)  # Show 25 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare period text for display
    days_diff = (fecha_hasta_dt - fecha_desde_dt).days
    if days_diff <= 1:
        periodo_texto = "Hoy"
    elif days_diff <= 7:
        periodo_texto = "Últimos 7 días"
    elif days_diff <= 30:
        periodo_texto = "Últimos 30 días"
    else:
        periodo_texto = f"Período de {days_diff} días"
    
    # Check if export was requested
    if request.GET.get('export') == '1':
        # Implement export functionality here
        # For example, return a CSV or Excel file
        pass
    
    context = {
        'transacciones': page_obj,
        'fecha_desde': fecha_desde_dt,
        'fecha_hasta': fecha_hasta_dt,
        'tipo_documento': tipo_documento,
        'total_ventas': total_ventas,

        
        'total_iva': total_iva,
        'total_facturas': total_facturas,
        'porcentaje_cambio': porcentaje_cambio,
        'ventas_chart_data': json.dumps(ventas_chart_data),  # Only include this once
        'periodo_texto': periodo_texto,
        'total_ventas_gravadas': total_ventas_gravadas,
        'proxima_declaracion': proxima_declaracion,
        'retenciones_recibidas': retenciones_recibidas,
        'retenciones_efectuadas': retenciones_efectuadas,
        'estado_ats': estado_ats,
        'page_obj': page_obj,
        
    }
    
    return render(request, 'reportes/ventas.html', context)

def iva_declaracion(request):
    """View for preparing IVA declaration"""
    # Get the current date range
    fecha_desde = request.GET.get('fecha_desde', None)
    fecha_hasta = request.GET.get('fecha_hasta', None)
    
    # If dates are provided, use them for the declaration
    if fecha_desde and fecha_hasta:
        # Fetch transactions for this period
        transacciones = Transaccion.objects.filter(
            fecha__gte=fecha_desde,
            fecha__lte=fecha_hasta
        )
        
        # Calculate totals
        total_ventas = sum(t.monto for t in transacciones)
        total_iva = 0
        for t in transacciones:
            total = float(t.monto)
            subtotal = total / 1.15
            iva = total - subtotal
            total_iva += iva
        
        context = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'total_ventas': total_ventas,
            'total_iva': total_iva,
            'total_ventas_gravadas': total_ventas - total_iva,
            'transacciones': transacciones
        }
        
        return render(request, 'reportes/iva_declaracion.html', context)
    
    # If no dates, redirect back with a message
    messages.warning(request, 'Por favor seleccione un rango de fechas para preparar la declaración')
    return redirect('reportes:ventas')

def ats(request):
    """View for downloading ATS file in XML format according to SRI requirements"""
    # Get the current date range
    fecha_desde = request.GET.get('fecha_desde', None)
    fecha_hasta = request.GET.get('fecha_hasta', None)
    
    if not fecha_desde or not fecha_hasta:
        messages.warning(request, 'Por favor seleccione un rango de fechas para generar el ATS')
        return redirect('reportes:ventas')
    
    # Convert string dates to datetime objects
    fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
    fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
    fecha_hasta_dt = datetime.combine(fecha_hasta_dt.date(), datetime.max.time())  # Set to end of day
    
    # Fetch transactions for this period
    transacciones = Transaccion.objects.filter(
        fecha__gte=fecha_desde_dt,
        fecha__lte=fecha_hasta_dt,
        procesado_pago=True,
        usuario_creador=request.user
    )
    
    # Create XML structure
    import xml.dom.minidom as minidom
    import xml.etree.ElementTree as ET
    
    # Create root element
    root = ET.Element("iva")
    
    # Add header information
    cabecera = ET.SubElement(root, "TipoIDInformante")
    cabecera.text = "R"  # R for RUC
    
    # Get business info from the business configuration
    from apps.configuraciones.models import BusinessConfiguration
    
    # Try to get the business configuration
    try:
        business_config = BusinessConfiguration.objects.first()
        
        # Get RUC directly from business configuration and ensure it's a string
        if business_config and business_config.ruc_negocio:
            ruc_to_use = str(business_config.ruc_negocio).strip()
            razon_social = business_config.nombre_negocio
        else:
            ruc_to_use = '9999999999999'
            razon_social = getattr(request.user, 'razon_social', request.user.get_full_name())
    except Exception as e:
        # Log the error and use default values
        print(f"Error retrieving business config: {e}")
        ruc_to_use = '9999999999999'
        razon_social = getattr(request.user, 'razon_social', request.user.get_full_name())
    
    id_informante = ET.SubElement(root, "IdInformante")
    id_informante.text = ruc_to_use
    
    razon_social_elem = ET.SubElement(root, "razonSocial")
    razon_social_elem.text = razon_social
    
    anio = ET.SubElement(root, "Anio")
    anio.text = fecha_desde_dt.strftime('%Y')
    
    mes = ET.SubElement(root, "Mes")
    mes.text = fecha_desde_dt.strftime('%m')
    
    # Add sales information
    ventas = ET.SubElement(root, "comprobantesEmitidos")
    
    # Group transactions by date for summary
    ventas_por_dia = {}
    for t in transacciones:
        fecha_str = t.fecha.strftime('%Y-%m-%d')
        if fecha_str in ventas_por_dia:
            ventas_por_dia[fecha_str].append(t)
        else:
            ventas_por_dia[fecha_str] = [t]
    
    # Add each day's transactions
    for fecha, trans_list in ventas_por_dia.items():
        # Calculate totals for the day
        total_dia = sum(float(t.monto) for t in trans_list)
        subtotal_dia = total_dia / 1.15
        iva_dia = total_dia - subtotal_dia
        
        # Create daily summary
        dia = ET.SubElement(ventas, "dia")
        
        fecha_elem = ET.SubElement(dia, "fecha")
        fecha_elem.text = fecha
        
        # Add transaction details
        for t in trans_list:
            total = float(t.monto)
            subtotal = total / 1.15
            iva = total - subtotal
            
            # Handle cases where venta or cliente might be None
            cliente_nombre = "Cliente General"
            cliente_id = "9999999999"
            
            if hasattr(t, 'venta') and t.venta is not None:
                if hasattr(t.venta, 'cliente') and t.venta.cliente is not None:
                    cliente_nombre = t.venta.cliente.nombre
                    # Convert cliente_id to string to avoid TypeError
                    cliente_id = str(t.venta.cliente.identificacion or "9999999999")
            
            # Ensure factura_id is a string
            factura_id = str(getattr(t, 'factuID', '-') or '-')
            
            # Create transaction element
            transaccion = ET.SubElement(dia, "comprobante")
            
            tipo_doc = ET.SubElement(transaccion, "tipoComprobante")
            tipo_doc.text = "01"  # 01 for Factura
            
            serie = ET.SubElement(transaccion, "serie")
            serie.text = factura_id[:6] if len(factura_id) >= 6 else "001001"
            
            secuencial = ET.SubElement(transaccion, "secuencial")
            secuencial.text = factura_id[6:] if len(factura_id) >= 6 else str(t.pk).zfill(9)
            
            fecha_emision = ET.SubElement(transaccion, "fechaEmision")
            fecha_emision.text = t.fecha.strftime('%d/%m/%Y')
            
            # Cliente information
            cliente = ET.SubElement(transaccion, "cliente")
            
            tipo_id_cliente = ET.SubElement(cliente, "tipoIdentificacion")
            # Ensure cliente_id is a string before checking length
            cliente_id_str = str(cliente_id).strip()
            tipo_id_cliente.text = "04" if len(cliente_id_str) == 10 else "01"
            
            id_cliente = ET.SubElement(cliente, "identificacion")
            id_cliente.text = cliente_id_str
            
            nombre_cliente = ET.SubElement(cliente, "razonSocial")
            nombre_cliente.text = cliente_nombre
            
            # Values
            valores = ET.SubElement(transaccion, "valores")
            
            base_imponible = ET.SubElement(valores, "baseImponible")
            base_imponible.text = f"{subtotal:.2f}"
            
            impuesto = ET.SubElement(valores, "impuesto")
            impuesto.text = f"{iva:.2f}"
            
            total_elem = ET.SubElement(valores, "total")
            total_elem.text = f"{total:.2f}"
    
    # Create pretty XML string
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    
    # Create response
    response = HttpResponse(xml_str, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename=ATS_{datetime.now().strftime("%Y%m%d")}.xml'
    
    return response