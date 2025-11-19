from django.shortcuts import render, redirect
from apps.productos.models import Producto, Categoria
import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required 
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from .models import Venta, DetalleVenta
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from apps.usuarios.models import Business
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
    except Business.DoesNotExist:
        modo_ventas = 'restaurante'  # Valor por defecto si no existe el negocio
    
    print(f"Modo de operación configurado en Business: {modo_ventas}")
    
    # Si hay una solicitud para cambiar el modo temporalmente (sesión)
    if request.GET.get('modo'):
        modo_ventas = request.GET.get('modo')
        request.session['modo_ventas'] = modo_ventas
        request.session.modified = True
        print(f"Modo temporalmente cambiado a: {modo_ventas} (solo para esta sesión)")
    
    # Si hay un modo en sesión, usarlo (temporal)
    modo_sesion = request.session.get('modo_ventas')
    if modo_sesion:
        modo_ventas = modo_sesion
        print(f"Usando modo temporal de sesión: {modo_ventas}")
    
    # Preparar contexto común para ambos modos
    if request.user.is_authenticated:
        productos = Producto.objects.filter(usuario_creador=request.user)
    else:
        productos = Producto.objects.all()
    
    categorias = Categoria.objects.filter(usuario_creador=request.user)
    
    # Get today's sales data for the dashboard
    today = timezone.now().date()
    ventas_hoy = Venta.objects.filter(fecha_hora__date=today, usuario_creador=request.user)
    
    total_ventas_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    num_ordenes_hoy = ventas_hoy.count()
    productos_vendidos_hoy = DetalleVenta.objects.filter(
        venta__fecha_hora__date=today,
        venta__usuario_creador=request.user
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'section_title': 'Ventas',
        'total_ventas_hoy': total_ventas_hoy,
        'num_ordenes_hoy': num_ordenes_hoy,
        'productos_vendidos_hoy': productos_vendidos_hoy,
        'ventas_recientes': ventas_hoy.order_by('-fecha_hora')[:5],
        'modo_actual': modo_ventas,
    }
    
    # Para el modo Retail, añadir clientes al contexto
    if modo_ventas == 'retail':
        from apps.clients.models import Cliente
        clientes = Cliente.objects.all().order_by('nombre')
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
            nombre__icontains=query
        )
    else:
        # If no query, return all products for the current user
        productos = Producto.objects.filter(
            usuario_creador=request.user
        )
    
    # Return JSON response or render template as needed
    # ...

@login_required
@require_POST
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
            
            # Create a new sale - in pending state
            nueva_venta = Venta.objects.create(
                usuario_creador=request.user,
                subtotal=0,
                iva=0,
                total=0,
                metodo_pago='cash'
            )
            
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
                    
                    # Create sale detail
                    DetalleVenta.objects.create(
                        venta=nueva_venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal_item
                    )
                    
                except Producto.DoesNotExist:
                    print(f"Producto con ID {producto_id} no encontrado")
                    continue
            
            # Calculate tax and total
            # Calculate total (no separate IVA calculation since prices already include IVA)
            from decimal import Decimal
            # Total is simply the sum of all product subtotals
            total = subtotal_venta
            iva = Decimal('0')  # Set IVA to 0 since it's already included in prices
            
            # Update the sale with calculated values
            nueva_venta.subtotal = subtotal_venta
            nueva_venta.iva = iva
            nueva_venta.total = total
            nueva_venta.save()
            
            # Get active clients for the client selection
            from apps.clients.models import Cliente
            clientes_activos = Cliente.objects.filter(estado=True)
            
            # Render the completar_venta template with the sale information
            context = {
                'venta': nueva_venta,
                'cart_items': cart_items_with_details,
                'subtotal': subtotal_venta,
                'iva': iva,
                'total': total,
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
    
    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        metodo_pago = request.POST.get('metodo_pago', 'cash')
        
        monto_recibido = Decimal('0.00')
        cambio = Decimal('0.00')
        
        if metodo_pago == 'cash':
            monto_recibido_str = request.POST.get('monto_recibido', '0.00')
            try:
                # Ensure monto_recibido is not None and is a valid decimal
                if monto_recibido_str and monto_recibido_str.strip():
                    monto_recibido = Decimal(monto_recibido_str)
                else:
                    monto_recibido = Decimal('0.00')
            except:
                monto_recibido = Decimal('0.00')
        
        try:
            venta = Venta.objects.get(id=venta_id, usuario_creador=request.user)
            
            # Ensure all required fields have default values
            if venta.total is None:
                venta.total = Decimal('0.00')
            if venta.subtotal is None:
                venta.subtotal = Decimal('0.00')
            if venta.iva is None:
                venta.iva = Decimal('0.00')
                
            venta.metodo_pago = metodo_pago
            venta.estado = 'completada'
            
            if metodo_pago == 'cash':
                # Ensure monto_recibido has a default value
                if monto_recibido is None:
                    monto_recibido = Decimal('0.00')
                    
                venta.monto_recibido = monto_recibido
                venta.cambio = max(monto_recibido - venta.total, Decimal('0.00'))
            
            # Get sale details to update product stock
            detalles_venta = DetalleVenta.objects.filter(venta=venta)
            
            # Update stock for each product in the sale
            for detalle in detalles_venta:
                producto = detalle.producto
                # Reduce stock by the quantity sold
                if producto.stock >= detalle.cantidad:
                    producto.stock -= detalle.cantidad
                    producto.save()
                else:
                    # If not enough stock, set stock to 0
                    producto.stock = 0
                    producto.save()
                    # Log the issue
                    print(f"Warning: Product {producto.nombre} (ID: {producto.id}) had insufficient stock. Requested: {detalle.cantidad}, Available: {producto.stock}")
            
            venta.save()
            
            # Create transaction
            transaccion = Transaccion.objects.create(
                venta=venta,
                monto=venta.total,
                metodo_pago=metodo_pago,
                fecha=timezone.now(),
                usuario_creador=request.user,
                procesado_pago=True
            )
            
            # Save the sale with the transaction ID
            venta.save()
            
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
    add_text("SouthernPOS", "Helvetica-Bold", title_size, "center")
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
        
        # To this:
        items = DetalleVenta.objects.filter(venta=venta)
        
        productos_sin_stock = []
        
        # Verificar stock para cada producto
        for item in items:
            producto = item.producto
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
    # Get all products for quick access - removed 'activo' filter since it doesn't exist
    productos = Producto.objects.all().order_by('nombre')
    
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

    