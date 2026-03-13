from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required 
from django.db.models import Sum, Count, F
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import json

from apps.productos.models import Producto, Categoria
from apps.usuarios.models import Business
from .models import Venta, DetalleVenta

@login_required
def ventas(request):
    """
    Vista principal de ventas que cambia según el modo seleccionado:
    - Restaurante: Muestra ventas.html
    - Retail: Muestra ventas_cajero.html
    """
    # Obtener el modo de operación del negocio del usuario
    try:
        business = Business.objects.get(user=request.user)
        modo_ventas = business.modo_operacion
        iva_porcentaje = business.iva_porcentaje
    except Business.DoesNotExist:
        modo_ventas = 'restaurante'  # Valor por defecto si no existe el negocio
        iva_porcentaje = 15  # Default 15% IVA para Ecuador
    
    # Si hay una solicitud para cambiar el modo temporalmente (sesión)
    if request.GET.get('modo'):
        modo_ventas = request.GET.get('modo')
        request.session['modo_ventas'] = modo_ventas
        request.session.modified = True
    
    # Si hay un modo en sesión, usarlo (temporal)
    modo_sesion = request.session.get('modo_ventas')
    if modo_sesion:
        modo_ventas = modo_sesion
    
    # Optimizar consultas con select_related y only
    # Filtrar productos: solo activos
    productos = Producto.objects.filter(
        usuario_creador=request.user,
        activo=True
    ).select_related('categoria').only(
        'id', 'nombre', 'precio_base', 'incluye_iva', 'imagen', 'categoria__nombre', 'stock', 'controla_stock', 'usuario_creador'
    )
    
    categorias = Categoria.objects.filter(
        usuario_creador=request.user
    ).only('id', 'nombre')
    
    # Get today's sales data for the dashboard - optimizado
    today = timezone.now().date()
    
    # Usar una sola consulta agregada
    stats_hoy = Venta.objects.filter(
        fecha_hora__date=today, 
        usuario_creador=request.user
    ).aggregate(
        total=Sum('total'),
        num_ordenes=Count('id')
    )
    
    total_ventas_hoy = stats_hoy['total'] or 0
    num_ordenes_hoy = stats_hoy['num_ordenes'] or 0
    
    # Productos vendidos hoy
    productos_vendidos_hoy = DetalleVenta.objects.filter(
        venta__fecha_hora__date=today,
        venta__usuario_creador=request.user
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Ventas recientes - optimizado con select_related
    ventas_recientes = Venta.objects.filter(
        fecha_hora__date=today,
        usuario_creador=request.user
    ).select_related('cliente').only(
        'id', 'total', 'fecha_hora', 'cliente__nombre'
    ).order_by('-fecha_hora')[:5]
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'section_title': 'Ventas',
        'total_ventas_hoy': total_ventas_hoy,
        'num_ordenes_hoy': num_ordenes_hoy,
        'productos_vendidos_hoy': productos_vendidos_hoy,
        'ventas_recientes': ventas_recientes,
        'modo_actual': modo_ventas,
        'iva_porcentaje': iva_porcentaje,
    }
    
    # Para el modo Retail, añadir clientes al contexto
    if modo_ventas == 'retail':
        from apps.clients.models import Cliente
        clientes = Cliente.objects.all().only('id', 'nombre').order_by('nombre')
        context['clientes'] = clientes
        context['title'] = 'Punto de Venta - Cajero'
        return render(request, 'ventas/ventas_cajero.html', context)
    
    # Por defecto, mostrar la vista de restaurante
    return render(request, 'ventas/ventas.html', context)
    

# Añadir vista para cambiar el modo (opcional - para API/AJAX)
@login_required
def cambiar_modo_ventas(request):
    """
    Vista para cambiar el modo de ventas via AJAX
    """
    if request.method == 'POST':
        modo = request.POST.get('modo', 'restaurante')
        if modo not in ['restaurante', 'retail']:
            modo = 'restaurante'
        
        # Guardar en la sesión
        request.session['modo_ventas'] = modo
        request.session.modified = True
        
        return JsonResponse({'success': True, 'modo': modo})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def buscar_productos_venta(request):
    query = request.GET.get('q', '')
    if query:
        # Filter products by both the search query AND the current user
        productos = Producto.objects.filter(
            usuario_creador=request.user,
            activo=True,
            nombre__icontains=query
        )
    else:
        # If no query, return all active products for the current user
        productos = Producto.objects.filter(
            usuario_creador=request.user,
            activo=True
        )
    
    # Return JSON response or render template as needed
    # ...

@login_required
@require_POST
@transaction.atomic
def completar_venta(request):
    """
    View to handle the checkout process and show the order summary
    """
    if request.method == 'POST':
        # Get cart data from the form
        cart_data = request.POST.get('cart_data', '[]')
        
        try:
            # Parse the JSON data
            cart_items = json.loads(cart_data)
            
            # Check if cart is empty
            if not cart_items:
                messages.error(request, 'El carrito está vacío. No se puede completar la venta.')
                return redirect('ventas:ventas')
            
            # 🎯 Obtener el Consumidor Final por defecto
            from apps.clients.models import Cliente
            consumidor_final = Cliente.get_consumidor_final(request.user)
            
            # 🎯 Obtener el negocio y punto de emisión del usuario
            try:
                business = Business.objects.get(user=request.user)
                # Obtener el punto de emisión activo (por defecto el primero)
                from apps.ventas.models import PuntoEmision
                punto_emision = PuntoEmision.objects.filter(
                    business=business,
                    activo=True
                ).first()
                
                # Si no existe punto de emisión, crear uno por defecto
                if not punto_emision:
                    punto_emision = PuntoEmision.objects.create(
                        business=business,
                        codigo='001',
                        establecimiento_codigo='001',
                        nombre='Caja Principal',
                        secuencial_actual=1,
                        activo=True
                    )
            except Business.DoesNotExist:
                business = None
                punto_emision = None
            
            # 🎯 Generar número de factura ANTES de crear la venta
            if punto_emision:
                # Usar select_for_update para prevenir race conditions
                punto_emision = PuntoEmision.objects.select_for_update().get(pk=punto_emision.pk)
                establecimiento = punto_emision.establecimiento_codigo
                codigo_punto = punto_emision.codigo
                secuencial = punto_emision.secuencial_actual
                numero_factura = f"{establecimiento}-{codigo_punto}-{secuencial:09d}"
            else:
                # Fallback si no hay punto de emisión
                establecimiento = '001'
                codigo_punto = '001'
                secuencial = 1
                numero_factura = f"{establecimiento}-{codigo_punto}-{secuencial:09d}"
            
            # Create a new sale with invoice number and Consumidor Final
            nueva_venta = Venta.objects.create(
                usuario_creador=request.user,
                cliente=consumidor_final,  # Siempre iniciar con Consumidor Final
                punto_emision=punto_emision,
                establecimiento_codigo=establecimiento,
                punto_emision_codigo=codigo_punto,
                secuencial=secuencial,
                numero_factura=numero_factura,
                subtotal=0,
                iva=0,
                total=0,
                metodo_pago='cash',
                tipo_comprobante='ticket',  # Por defecto ticket
                estado_sri='PENDIENTE'
            )
            
            # 🎯 Incrementar secuencial DESPUÉS de crear la venta
            if punto_emision:
                punto_emision.secuencial_actual = F('secuencial_actual') + 1
                punto_emision.save(update_fields=['secuencial_actual'])
                # 🔥 Refrescar desde DB para tener el valor actualizado
                punto_emision.refresh_from_db()
            
            # Process each item in the cart
            subtotal_venta = 0
            cart_items_with_details = []
            
            for item in cart_items:
                producto_id = item.get('id')
                cantidad = item.get('quantity', 0)
                
                # Skip invalid items
                if not producto_id or cantidad <= 0:
                    continue
                
                # Get the product from the database
                try:
                    producto = Producto.objects.get(id=producto_id)
                    
                    # Calculate subtotal for this item
                    precio_unitario = producto.precio
                    subtotal_item = precio_unitario * cantidad
                    subtotal_venta += subtotal_item
                    
                    # Add to cart items with details for display
                    cart_items_with_details.append({
                        'id': producto_id,
                        'nombre': producto.nombre,
                        'precio': precio_unitario,
                        'quantity': cantidad,
                        'subtotal': subtotal_item
                    })
                    
                    # Create sale detail con información histórica completa
                    DetalleVenta.objects.create(
                        venta=nueva_venta,
                        producto=producto,
                        nombre_producto=producto.nombre,
                        codigo_producto=producto.codigo_barras,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        costo_unitario=producto.costo if producto.costo else Decimal('0'),
                        subtotal=subtotal_item,
                        iva_porcentaje=producto.get_iva_porcentaje()
                    )
                    
                except Producto.DoesNotExist:
                    print(f"Producto con ID {producto_id} no encontrado")
                    continue
            
            # Calculate tax and total
            # Prices include IVA, we need to break it down
            from decimal import Decimal
            
            # Get IVA rate from business settings (default 15% for Ecuador)
            try:
                business = Business.objects.get(user=request.user)
                tax_rate = business.iva_porcentaje / Decimal('100')  # Convert percentage to decimal
            except Business.DoesNotExist:
                tax_rate = Decimal('0.15')  # Default 15% IVA for Ecuador (vigente desde abril 2024)
            
            # Calculate base (subtotal without IVA) and IVA
            # Since prices include IVA: base = total_with_iva / (1 + tax_rate)
            total_con_iva = subtotal_venta
            base_sin_iva = total_con_iva / (Decimal('1') + tax_rate)
            iva_calculado = total_con_iva - base_sin_iva
            
            # Round to 2 decimals
            base_sin_iva = base_sin_iva.quantize(Decimal('0.01'))
            iva_calculado = iva_calculado.quantize(Decimal('0.01'))
            
            # Update the sale with calculated values
            nueva_venta.subtotal = base_sin_iva  # Base without IVA
            nueva_venta.iva = iva_calculado      # IVA amount
            nueva_venta.total = total_con_iva    # Total with IVA (what customer pays)
            nueva_venta.save()
            
            # Get active clients for the client selection
            from apps.clients.models import Cliente
            clientes_activos = Cliente.objects.filter(estado=True)
            
            # Render the completar_venta template with the sale information
            context = {
                'venta': nueva_venta,
                'cart_items': cart_items_with_details,
                'subtotal': base_sin_iva,
                'iva': iva_calculado,
                'total': total_con_iva,
                'clientes_activos': clientes_activos
            }
            
            return render(request, 'ventas/completar_venta.html', context)
            
        except json.JSONDecodeError as e:
            messages.error(request, f'Error al procesar los datos del carrito: {str(e)}')
            return redirect('ventas:ventas')
        except Exception as e:
            print(f"Error processing sale: {str(e)}")
            messages.error(request, f'Error al procesar la venta: {str(e)}')
            return redirect('ventas:ventas')
    
    # If not POST or any other issue
    return redirect('ventas:ventas')

@login_required
@require_POST
# In the procesar_pago view
def procesar_pago(request):
    """
    View to process the payment and complete the sale
    """
    from decimal import Decimal
    from apps.transacciones.models import Transaccion
    from .services import OrderService
    
    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        metodo_pago = request.POST.get('metodo_pago', 'cash')
        cliente_id = request.POST.get('cliente_id', None)
        
        monto_recibido = Decimal('0.00')
        cambio = Decimal('0.00')
        
        if metodo_pago == 'cash':
            monto_recibido_str = request.POST.get('monto_recibido', '0.00')
            try:
                if monto_recibido_str and monto_recibido_str.strip():
                    monto_recibido = Decimal(monto_recibido_str)
                else:
                    monto_recibido = Decimal('0.00')
            except:
                monto_recibido = Decimal('0.00')
        
        try:
            venta = Venta.objects.get(id=venta_id, usuario_creador=request.user)
            
            # 🎯 El cliente ya está aplicado desde completar_venta o aplicar_cliente_descuentos
            # NO volver a aplicar aquí para no perder el cliente seleccionado
            # Solo guardamos el método de pago y procesamos
            
            print(f"DEBUG procesar_pago - Venta ID: {venta.id}")
            print(f"DEBUG procesar_pago - Cliente: {venta.cliente.nombre if venta.cliente else 'None'}")
            print(f"DEBUG procesar_pago - Descuento: ${venta.descuento_total}")
            print(f"DEBUG procesar_pago - Recargo: ${venta.recargo_total}")
            print(f"DEBUG procesar_pago - Total: ${venta.total}")
            
            # 🎯 VALIDAR CRÉDITO
            if metodo_pago == 'credit':
                # Consumidor Final NO puede comprar a crédito
                if not venta.cliente or venta.cliente.es_consumidor_final():
                    messages.error(request, 'Consumidor Final no puede comprar a crédito. Seleccione un cliente registrado.')
                    return redirect('ventas:completar_venta')
                
                # Verificar que el cliente tenga crédito habilitado y cupo disponible
                if not venta.cliente.puede_comprar_a_credito(venta.total):
                    messages.error(request, 'Este cliente no tiene crédito habilitado o cupo suficiente.')
                    return redirect('ventas:completar_venta')
                
                # Configurar venta a crédito
                venta.estado_pago = 'pendiente'
                venta.saldo_pendiente = venta.total
            else:
                # Pago inmediato (efectivo, tarjeta, transferencia)
                # Consumidor Final solo puede pagar inmediato
                venta.estado_pago = 'pagado'
                venta.saldo_pendiente = Decimal('0.00')
            
            # Obtener el negocio del usuario
            try:
                business = Business.objects.get(user=request.user)
            except Business.DoesNotExist:
                business = None
            
            # Ensure all required fields have default values
            if venta.total is None:
                venta.total = Decimal('0.00')
            if venta.subtotal is None:
                venta.subtotal = Decimal('0.00')
            if venta.iva is None:
                venta.iva = Decimal('0.00')
                
            venta.metodo_pago = metodo_pago
            
            if metodo_pago == 'cash':
                if monto_recibido is None:
                    monto_recibido = Decimal('0.00')
                    
                venta.monto_recibido = monto_recibido
                venta.cambio = max(monto_recibido - venta.total, Decimal('0.00'))
            
            # Get sale details to update product stock
            detalles_venta = DetalleVenta.objects.filter(venta=venta)
            
            # Update stock for each product in the sale (only if they control stock)
            for detalle in detalles_venta:
                producto = detalle.producto
                # Solo reducir stock si el producto controla inventario
                if producto.controla_stock and producto.stock is not None:
                    # Reduce stock by the quantity sold
                    if producto.stock >= detalle.cantidad:
                        producto.stock -= detalle.cantidad
                        producto.save()
                    else:
                        # If not enough stock, set stock to 0
                        producto.stock = 0
                        producto.save()
                        print(f"Warning: Product {producto.nombre} (ID: {producto.id}) had insufficient stock. Requested: {detalle.cantidad}, Available: {producto.stock}")
            
            venta.save()
            
            # 🎯 Actualizar estadísticas del cliente (excepto Consumidor Final)
            if venta.cliente and not venta.cliente.es_consumidor_final():
                venta.cliente.actualizar_estadisticas_compra(venta.total)
            
            #  Create transaction with snapshot
            tipo_transaccion = 'venta'
            monto_transaccion = venta.total if metodo_pago != 'credit' else Decimal('0.00')
            
            transaccion = Transaccion.objects.create(
                venta=venta,
                cliente=venta.cliente,
                tipo_transaccion=tipo_transaccion,
                monto=monto_transaccion,
                venta_total_snapshot=venta.total,  # Guardar snapshot
                metodo_pago=metodo_pago,
                fecha=timezone.now(),
                usuario_creador=request.user,
                procesado_pago=True if metodo_pago != 'credit' else False
            )
            
            return redirect('ventas:venta_completa', venta_id=venta.id)

        except Venta.DoesNotExist:
            messages.error(request, 'La venta no existe o no tienes permiso para acceder a ella.')
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {str(e)}')
        
        return redirect('ventas:ventas')

@login_required
def venta_completa(request, venta_id):
    """
    View to display a completed sale
    """
    try:
        # Get the sale from the database
        venta = get_object_or_404(Venta, id=venta_id)
        
        # Get the sale details
        detalles = DetalleVenta.objects.filter(venta=venta)
        
        # Get the transaction associated with this sale
        from apps.transacciones.models import Transaccion
        transaccion = Transaccion.objects.filter(venta=venta).first()
        
        # Debug logging
        print(f"Venta ID: {venta_id}, Total: {venta.total}")
        print(f"Número de detalles encontrados: {detalles.count()}")
        for detalle in detalles:
            print(f"Producto: {detalle.producto.nombre}, Cantidad: {detalle.cantidad}, Subtotal: {detalle.subtotal}")
        
        # Add client information debugging - with hasattr check
        if hasattr(venta, 'cliente') and venta.cliente:
            print(f"Cliente: {venta.cliente.nombre}, ID: {venta.cliente.identificacion}")
        else:
            print("Cliente: Consumidor Final")
        
        context = {
            'venta': venta,
            'detalles': detalles,
            'section_title': 'Venta Completada',  # Add section title
            'transaccion': transaccion,  # Add transaction to context
        }
        
        return render(request, 'ventas/venta_completa.html', context)
    except Exception as e:
        print(f"Error in venta_completa: {str(e)}")
        messages.error(request, f"Error al mostrar la venta: {str(e)}")
        return redirect('ventas:ventas')

@login_required
def descargar_factura(request, venta_id):
    """
    View to generate and download a PDF invoice for a sale in thermal receipt format (80mm width)
    """
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import mm, inch
    from .models import Venta, DetalleVenta
    import io
    
    # Get the sale from the database
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Get the sale details
    detalles = DetalleVenta.objects.filter(venta=venta)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Define thermal receipt dimensions (80mm width)
    receipt_width = 80 * mm
    receipt_height = 200 * mm  # Shorter height for more compact receipt
    
    # Create the PDF object with custom size
    p = canvas.Canvas(buffer, pagesize=(receipt_width, receipt_height))
    
    # Set up the PDF document
    p.setTitle(f"Ticket #{venta.id}")
    
    # Starting y position (from top)
    y_pos = receipt_height - 10 * mm
    
    # Set font sizes for thermal receipt
    title_size = 12
    header_size = 9
    normal_size = 8
    small_size = 7
    
    # Function to add text and update y position
    def add_text(text, font="Helvetica", size=normal_size, align="left", y_offset=4*mm):
        nonlocal y_pos
        p.setFont(font, size)
        if align == "center":
            p.drawCentredString(receipt_width/2, y_pos, text)
        elif align == "right":
            p.drawRightString(receipt_width - 5*mm, y_pos, text)
        else:
            p.drawString(5*mm, y_pos, text)
        y_pos -= y_offset
        return y_pos
    
    # Function to add a dashed line instead of solid line
    def add_line(y_offset=3*mm):
        nonlocal y_pos
        p.setDash([2, 2], 0)  # Create a dashed line pattern
        p.line(5*mm, y_pos, receipt_width - 5*mm, y_pos)
        p.setDash([], 0)  # Reset to solid line
        y_pos -= y_offset
        return y_pos
    
    # Add company header
    add_text("Lemon POS", "Helvetica-Bold", title_size, "center")
    add_text("Av. Amazonas 123, Quito, Ecuador", "Helvetica", small_size, "center", 3*mm)
    add_text("Teléfono: +593 987 654 321", "Helvetica", small_size, "center", 3*mm)
    add_text("RUC: 1790012345001", "Helvetica", small_size, "center", 3*mm)
    
    # Add separator - ensure there's space before the line
    y_pos -= 1*mm  # Add a bit more space before the line
    add_line()
    
    # Add invoice details
    add_text(f"TICKET #{venta.id}", "Helvetica-Bold", header_size, "center")
    add_text(f"Fecha: {venta.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}", "Helvetica", small_size, "center", 3*mm)
    
    # Add separator
    y_pos -= 1*mm  # Add a bit more space before the line
    add_line()
    
    # Add customer information
    add_text("CLIENTE:", "Helvetica-Bold", header_size)
    if hasattr(venta, 'cliente') and venta.cliente:
        add_text(venta.cliente.nombre, "Helvetica", normal_size, "left", 3*mm)
        add_text(f"ID/RUC: {venta.cliente.identificacion}", "Helvetica", normal_size, "left", 3*mm)
        if venta.cliente.direccion:
            add_text(f"Dir: {venta.cliente.direccion}", "Helvetica", small_size, "left", 3*mm)
            if venta.cliente.ciudad:
                add_text(f"Ciudad: {venta.cliente.ciudad}", "Helvetica", small_size, "left", 3*mm)
    else:
        add_text("Consumidor Final", "Helvetica", normal_size, "left", 3*mm)
    
    # Add separator
    y_pos -= 1*mm  # Add a bit more space before the line
    add_line()
    
    # Add table headers for items
    add_text("DETALLE DE COMPRA:", "Helvetica-Bold", header_size, "left")
    y_pos -= 2*mm  # Add space after the header
    
    # Column headers
    p.setFont("Helvetica-Bold", small_size)
    p.drawString(5*mm, y_pos, "Producto")
    p.drawString(40*mm, y_pos, "Cant")
    p.drawString(50*mm, y_pos, "Precio")
    p.drawString(65*mm, y_pos, "Total")
    y_pos -= 3*mm
    
    # Add a line under the headers - thinner line for column headers
    p.setLineWidth(0.5)
    p.line(5*mm, y_pos, receipt_width - 5*mm, y_pos)
    p.setLineWidth(1)
    y_pos -= 3*mm
    
    # Add items
    p.setFont("Helvetica", small_size)
    for detalle in detalles:
        # Check if we need to add a new page
        if y_pos < 30*mm:
            p.showPage()
            y_pos = receipt_height - 15*mm
            p.setFont("Helvetica", small_size)
        
        # Product name (truncate if too long)
        product_name = detalle.producto.nombre
        if len(product_name) > 20:
            product_name = product_name[:17] + "..."
        p.drawString(5*mm, y_pos, product_name)
        
        # Quantity, price and subtotal
        p.drawString(40*mm, y_pos, str(detalle.cantidad))
        p.drawString(50*mm, y_pos, f"${float(detalle.precio_unitario):.2f}")
        p.drawString(65*mm, y_pos, f"${float(detalle.subtotal):.2f}")
        y_pos -= 3*mm
    
    # Add a line under the items - use dotted line
    p.setDash([1, 1], 0)
    p.line(5*mm, y_pos, receipt_width - 5*mm, y_pos)
    p.setDash([], 0)
    y_pos -= 3*mm
    
    # Add totals
    p.setFont("Helvetica-Bold", small_size)
    p.drawString(40*mm, y_pos, "Subtotal:")
    p.drawString(65*mm, y_pos, f"${float(venta.subtotal):.2f}")
    y_pos -= 3*mm
    
    p.drawString(40*mm, y_pos, "IVA (12%):")
    p.drawString(65*mm, y_pos, f"${float(venta.iva):.2f}")
    y_pos -= 3*mm
    
    # Total with a highlight box
    p.setFillColorRGB(0.9, 0.9, 0.9)  # Light gray background
    p.rect(38*mm, y_pos - 1*mm, 37*mm, 4*mm, fill=1, stroke=0)
    p.setFillColorRGB(0, 0, 0)  # Back to black text
    
    p.setFont("Helvetica-Bold", header_size)
    p.drawString(40*mm, y_pos, "TOTAL:")
    p.drawString(65*mm, y_pos, f"${float(venta.total):.2f}")
    y_pos -= 5*mm
    
    # Payment method
    p.setFont("Helvetica", normal_size)
    metodo_pago_display = "Efectivo" if venta.metodo_pago == "cash" else "Tarjeta"
    p.drawString(5*mm, y_pos, f"Método de Pago: {metodo_pago_display}")
    y_pos -= 3*mm
    
    if venta.metodo_pago == 'cash':
        p.drawString(5*mm, y_pos, f"Monto Recibido: ${float(venta.monto_recibido):.2f}")
        y_pos -= 3*mm
        p.drawString(5*mm, y_pos, f"Cambio: ${float(venta.cambio):.2f}")
        y_pos -= 3*mm
    
    # Add separator - use a different style for the final separator
    y_pos -= 1*mm
    p.setDash([4, 2], 0)  # Longer dashes
    p.line(5*mm, y_pos, receipt_width - 5*mm, y_pos)
    p.setDash([], 0)
    y_pos -= 4*mm
    
    # Add footer
    p.setFont("Helvetica-Bold", small_size)
    p.drawCentredString(receipt_width/2, y_pos, "¡Gracias por su compra!")
    y_pos -= 4*mm
    
    p.setFont("Helvetica", small_size)
    p.drawCentredString(receipt_width/2, y_pos, "Para devoluciones, presente este")
    y_pos -= 3*mm
    p.drawCentredString(receipt_width/2, y_pos, "comprobante dentro de los próximos 7 días.")
    y_pos -= 4*mm
    
    # Add QR code simulation (just a placeholder box)
    qr_size = 15*mm
    p.rect((receipt_width - qr_size)/2, y_pos - qr_size, qr_size, qr_size, stroke=1, fill=0)
    p.setFont("Helvetica", 6)
    p.drawCentredString(receipt_width/2, y_pos - qr_size - 3*mm, "Factura Electrónica")
    y_pos = y_pos - qr_size - 6*mm
    
    p.drawCentredString(receipt_width/2, y_pos, "Contacto: +593 987 654 321")
    y_pos -= 3*mm
    p.drawCentredString(receipt_width/2, y_pos, "contacto@southernfood.ec")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{venta.id}.pdf"'
    response.write(pdf)
    
    return response


def venta_completa_sin_id(request):
    """
    View to display a completed sale
    This is used when redirecting from completar_venta
    """
    # Get the most recent sale from the database
    try:
        venta = Venta.objects.order_by('-fecha_hora').first()
        
        if not venta:
            # If no sales found, redirect to the sales page
            return redirect('ventas:ventas')
        
        # Redirect to the venta_completa view with the actual ID
        return redirect('ventas:venta_completa', venta_id=venta.id)
        
    except Exception as e:
        # Log the error and redirect to the sales page
        print(f"Error retrieving sale: {e}")
        return redirect('ventas:ventas')


# Add this import if not already present
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Venta, DetalleVenta

@csrf_exempt
@require_POST
def verificar_stock(request):
    try:
        data = json.loads(request.body)
        venta_id = data.get('venta_id')
        
        # Obtener la venta y sus items
        venta = Venta.objects.get(id=venta_id)
        # Change any code like this:
        items = DetalleVenta.objects.filter(venta=venta)
        
        productos_sin_stock = []
        
        # Verificar stock para cada producto (solo si controla stock)
        for item in items:
            producto = item.producto
            # Solo verificar stock si el producto controla inventario
            if producto.controla_stock and producto.stock is not None:
                if producto.stock < item.cantidad:
                    productos_sin_stock.append(f"{producto.nombre} (Disponible: {producto.stock}, Requerido: {item.cantidad})")
        
        if productos_sin_stock:
            return JsonResponse({
                'success': False,
                'productos_sin_stock': productos_sin_stock
            })
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        print(f"Error en verificar_stock: {str(e)}")  # Log the error for debugging
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Add this new view
def actualizar_cliente_venta(request, venta_id):
    """Update the client for a sale"""
    if request.method == 'POST':
        try:
            venta = Venta.objects.get(id=venta_id)
            cliente_id = request.POST.get('client_id')
            
            if cliente_id:
                from apps.clients.models import Cliente
                cliente = Cliente.objects.get(id=cliente_id)
                venta.cliente = cliente
                # Log the client assignment for debugging
                print(f"Assigned client {cliente.nombre} (ID: {cliente.id}) to sale {venta_id}")
                venta.save()
                return JsonResponse({'success': True})
            else:
                # If no client ID, set to None (Consumidor Final)
                venta.cliente = None
                venta.save()
                print(f"Removed client from sale {venta_id} (Consumidor Final)")
                return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error updating client for sale {venta_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ventas_cajero(request):
    """
    View for the cashier interface.
    Renders the ventas_cajero.html template with necessary context.
    """
    # Get all active products for quick access
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    
    # Get all customers for the customer selection modal
    from apps.clients.models import Cliente
    clientes = Cliente.objects.all().order_by('nombre')
    
    # Get categories for filtering products
    categorias = Categoria.objects.all()
    
    context = {
        'productos': productos,
        'clientes': clientes,
        'categorias': categorias,
        'title': 'Punto de Venta - Cajero',
    }
    
    return render(request, 'ventas/ventas_cajero.html', context)


# Vista para procesar pagos de crédito
@login_required
@require_POST
def procesar_pago_credito(request):
    """Procesa pagos posteriores para ventas a crédito"""
    try:
        data = json.loads(request.body)
        venta_id = data.get('venta_id')
        monto = data.get('monto')
        metodo_pago = data.get('metodo_pago', 'cash')
        referencia = data.get('referencia', None)
        
        # Validaciones
        if not venta_id or not monto:
            return JsonResponse({
                'success': False,
                'error': 'Venta ID y monto son requeridos'
            }, status=400)
        
        venta = get_object_or_404(Venta, id=venta_id, usuario_creador=request.user)
        
        # Validar que la venta tenga saldo pendiente
        if venta.saldo_pendiente <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Esta venta no tiene saldo pendiente'
            }, status=400)
        
        # Aplicar el pago
        transaccion = venta.aplicar_pago(
            monto=monto,
            metodo_pago=metodo_pago,
            referencia=referencia
        )
        
        return JsonResponse({
            'success': True,
            'transaccion_id': transaccion.transaction_id,
            'saldo_pendiente': float(venta.saldo_pendiente),
            'estado_pago': venta.estado_pago,
            'monto_pagado': float(monto)
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar pago: {str(e)}'
        }, status=500)


# Vista para listar ventas con saldo pendiente (créditos)
@login_required
def ventas_credito(request):
    """Lista todas las ventas a crédito con saldo pendiente"""
    ventas_pendientes = Venta.objects.filter(
        usuario_creador=request.user,
        saldo_pendiente__gt=0
    ).select_related('cliente').order_by('-fecha_hora')
    
    context = {
        'ventas_pendientes': ventas_pendientes,
        'section_title': 'Ventas a Crédito'
    }
    
    return render(request, 'ventas/ventas_credito.html', context)



@login_required
@require_POST
def aplicar_cliente_descuentos(request):
    """
    Aplica descuentos/recargos del cliente y retorna información actualizada
    """
    try:
        data = json.loads(request.body)
        venta_id = data.get('venta_id')
        cliente_id = data.get('cliente_id')
        
        venta = get_object_or_404(Venta, id=venta_id, usuario_creador=request.user)
        
        if not cliente_id:
            return JsonResponse({
                'success': False,
                'error': 'Cliente ID requerido'
            }, status=400)
        
        from apps.clients.models import Cliente
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        # Actualizar cliente en la venta
        venta.cliente = cliente
        
        # Calcular descuentos y recargos según método profesional (Factus, Contífico, Odoo)
        from decimal import Decimal, ROUND_HALF_UP
        
        print(f"=== APLICAR DESCUENTOS/RECARGOS (Método Profesional SRI) ===")
        print(f"Cliente: {cliente.nombre}")
        print(f"Tasa descuento: {cliente.tasa_descuento}%")
        print(f"Tasa recargo: {cliente.tasa_recargo}%")
        
        # Paso 1: Calcular subtotal SIN IVA (con alta precisión)
        subtotal_sin_iva = Decimal('0')
        iva_rate = Decimal(str(request.user.business.iva_porcentaje)) / Decimal('100')
        
        for item in venta.detalleventa_set.all():
            precio_total_item = item.precio_unitario * item.cantidad
            # Extraer IVA con precisión completa
            precio_sin_iva = precio_total_item / (Decimal('1') + iva_rate)
            subtotal_sin_iva += precio_sin_iva
        
        print(f"Paso 1 - Subtotal SIN IVA: ${subtotal_sin_iva}")
        
        # Paso 2: Aplicar DESCUENTO (encadenado)
        descuento_cliente = Decimal('0')
        subtotal_con_descuento = subtotal_sin_iva
        
        if cliente.tasa_descuento > 0:
            tasa_desc = Decimal(str(cliente.tasa_descuento)) / Decimal('100')
            descuento_cliente = subtotal_sin_iva * tasa_desc
            subtotal_con_descuento = subtotal_sin_iva - descuento_cliente
            print(f"Paso 2 - Descuento ({cliente.tasa_descuento}%): -${descuento_cliente}")
            print(f"         Subtotal después descuento: ${subtotal_con_descuento}")
        
        # Paso 3: Aplicar RECARGO sobre el subtotal YA descontado (encadenado)
        recargo_cliente = Decimal('0')
        base_imponible = subtotal_con_descuento
        
        if cliente.tasa_recargo > 0:
            tasa_rec = Decimal(str(cliente.tasa_recargo)) / Decimal('100')
            recargo_cliente = subtotal_con_descuento * tasa_rec
            base_imponible = subtotal_con_descuento + recargo_cliente
            print(f"Paso 3 - Recargo ({cliente.tasa_recargo}%): +${recargo_cliente}")
            print(f"         Base imponible final: ${base_imponible}")
        
        # Paso 4: Calcular IVA sobre la base imponible final
        iva_calculado = base_imponible * iva_rate
        print(f"Paso 4 - IVA ({request.user.business.iva_porcentaje}%): ${iva_calculado}")
        
        # Paso 5: Calcular TOTAL
        total_final = base_imponible + iva_calculado
        print(f"Paso 5 - TOTAL: ${total_final}")
        
        # Guardar con precisión completa (Decimal mantiene precisión)
        venta.subtotal = subtotal_sin_iva  # Subtotal original antes de ajustes
        venta.descuento_total = descuento_cliente
        venta.recargo_total = recargo_cliente
        venta.iva = iva_calculado
        venta.total = total_final
        
        print(f"=== Resumen ===")
        print(f"Subtotal: ${subtotal_sin_iva}")
        print(f"Descuento: -${descuento_cliente}")
        print(f"Recargo: +${recargo_cliente}")
        print(f"Base: ${base_imponible}")
        print(f"IVA: ${iva_calculado}")
        print(f"TOTAL: ${total_final}")
        print(f"=========================")
        
        venta.save()
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'cliente': {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'identificacion': cliente.identificacion,
                'grupo': cliente.get_grupo_display(),
                'estado': cliente.get_estado_display(),
                'credito_dias': cliente.credito,
                'cupo': float(cliente.cupo),
                'tasa_descuento': float(cliente.tasa_descuento),
                'tasa_recargo': float(cliente.tasa_recargo),
                'puede_credito': cliente.puede_comprar_a_credito(total_final),
                'es_consumidor_final': cliente.es_consumidor_final()
            },
            'totales': {
                'subtotal': float(venta.subtotal),
                'descuento_total': float(venta.descuento_total),
                'recargo_total': float(venta.recargo_total),
                'iva': float(venta.iva),
                'total': float(venta.total)
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
