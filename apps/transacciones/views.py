from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from apps.ventas.models import Venta, DetalleVenta
from .models import Transaccion

@login_required
def lista_transacciones(request):
    # Get query parameters
    query = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    metodo_pago = request.GET.get('metodo_pago', '')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Get transactions for the current user
    transacciones = Transaccion.objects.filter(
        usuario_creador=request.user,
        procesado_pago=True
    ).select_related('venta', 'venta__cliente', 'venta__order').order_by('-fecha')
    
    # Apply search filters - busca en TODOS los campos
    if query:
        transacciones = transacciones.filter(
            Q(transaction_id__icontains=query) |
            Q(factuID__icontains=query) |
            Q(venta__order__order_number__icontains=query) |
            Q(venta__cliente__nombre__icontains=query) |
            Q(venta__cliente__identificacion__icontains=query) |
            Q(monto__icontains=query) |
            Q(fecha__icontains=query)
        )

    if fecha_inicio:
        transacciones = transacciones.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        transacciones = transacciones.filter(fecha__lte=fecha_fin)
    if metodo_pago:
        transacciones = transacciones.filter(metodo_pago=metodo_pago)

    # Si es AJAX, devolver JSON
    if is_ajax:
        html = render_to_string('transacciones/partials/transactions_table_rows.html', {
            'transacciones': transacciones[:50],
            'currency_symbol': request.user.business.moneda if hasattr(request.user, 'business') else '$',
            'request': request
        })
        return JsonResponse({
            'html': html,
            'count': transacciones.count()
        })

    # Pagination
    paginator = Paginator(transacciones, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transacciones': page_obj,
        'query': query,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'metodo_pago': metodo_pago,
        'section_title': 'Historial de Transacciones'
    }
    
    return render(request, 'transacciones/lista_transacciones.html', context)

@login_required
def detalle_transaccion(request, transaccion_id):
    """Vista para mostrar el detalle de una transacción específica."""
    transaccion = get_object_or_404(Transaccion, transaction_id=transaccion_id, usuario_creador=request.user)
    venta = transaccion.venta
    detalles = DetalleVenta.objects.filter(venta=venta)
    
    is_mobile = 'Mobile' in request.META.get('HTTP_USER_AGENT', '') or 'Android' in request.META.get('HTTP_USER_AGENT', '')
    
    context = {
        'transaccion': transaccion,
        'venta': venta,
        'detalles': detalles,
        'section_title': f'Detalle de Transacción #{transaccion.transaction_id}',
        'is_mobile': is_mobile,
    }
    
    return render(request, 'transacciones/detalle_transaccion.html', context)

@login_required
def buscar_transacciones(request):
    """API para buscar transacciones (para AJAX)."""
    query = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    metodo_pago = request.GET.get('metodo_pago', '')

    # Get only completed transactions for the current user
    transacciones = Transaccion.objects.filter(
        usuario_creador=request.user,
        procesado_pago=True
    ).select_related('venta', 'venta__cliente', 'venta__order').order_by('-fecha')

    if query:
        transacciones = transacciones.filter(
            Q(transaction_id__icontains=query) |
            Q(factuID__icontains=query) |
            Q(venta__order__order_number__icontains=query) |
            Q(venta__cliente__nombre__icontains=query) |
            Q(venta__cliente__identificacion__icontains=query) |
            Q(monto__icontains=query)
        )

    if fecha_inicio:
        transacciones = transacciones.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        transacciones = transacciones.filter(fecha__lte=fecha_fin)
    if metodo_pago:
        transacciones = transacciones.filter(metodo_pago=metodo_pago)

    # Devolver HTML parcial para AJAX
    html = render_to_string('transacciones/partials/transactions_table_rows.html', {
        'transacciones': transacciones[:50],
        'currency_symbol': request.user.business.moneda if hasattr(request.user, 'business') else '$',
        'request': request
    })
    
    return JsonResponse({
        'html': html,
        'count': transacciones.count()
    })


def procesar_pago(request, transaccion_id):
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id)
        
        # Your payment processing logic here...
        # If payment is successful:
        transaccion.procesado_pago = True
        transaccion.save()
        
        return JsonResponse({'status': 'success', 'message': 'Pago procesado correctamente'})
    except Transaccion.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Transacción no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
