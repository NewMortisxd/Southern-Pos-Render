from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.ventas.models import Venta, DetalleVenta
from .models import Transaccion

@login_required
def lista_transacciones(request):
    # Get query parameters
    query = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    metodo_pago = request.GET.get('metodo_pago', '')

    # Get transactions for the current user
    transacciones = Transaccion.objects.filter(
        usuario_creador=request.user,
        procesado_pago=True
    ).order_by('-fecha')
    
    # Apply search filters if provided
    if query:
        transacciones = transacciones.filter(
            Q(transaction_id__icontains=query) |
            Q(factuID__icontains=query) |
            Q(venta__cliente__nombre__icontains=query) |
            Q(venta__cliente__identificacion__icontains=query)
        )

    if fecha_inicio:
        transacciones = transacciones.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        transacciones = transacciones.filter(fecha__lte=fecha_fin)
    if metodo_pago:
        transacciones = transacciones.filter(metodo_pago=metodo_pago)

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
        'section_title': 'Historial de Transacciones'  # Add this line to set the section title
    }
    
    return render(request, 'transacciones/lista_transacciones.html', context)

@login_required
def detalle_transaccion(request, transaccion_id):
    """Vista para mostrar el detalle de una transacción específica."""
    # Get the transaction only if it belongs to the current user
    transaccion = get_object_or_404(Transaccion, transaction_id=transaccion_id, usuario_creador=request.user)
    venta = transaccion.venta
    detalles = DetalleVenta.objects.filter(venta=venta)
    
    # Detectar si es una solicitud móvil (simplificado)
    is_mobile = 'Mobile' in request.META.get('HTTP_USER_AGENT', '') or 'Android' in request.META.get('HTTP_USER_AGENT', '')
    
    context = {
        'transaccion': transaccion,
        'venta': venta,
        'detalles': detalles,
        'section_title': f'Detalle de Transacción #{transaccion.transaction_id}',  # Add section title here
        'is_mobile': is_mobile,  # Pasar al template si es móvil
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
    ).order_by('-fecha')

    if query:
        transacciones = transacciones.filter(
            Q(transaction_id__icontains=query) |
            Q(factuID__icontains=query) |
            Q(venta__cliente__nombre__icontains=query) |
            Q(venta__cliente__identificacion__icontains=query)
        )

    if fecha_inicio:
        transacciones = transacciones.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        transacciones = transacciones.filter(fecha__lte=fecha_fin)
    if metodo_pago:
        transacciones = transacciones.filter(metodo_pago=metodo_pago)

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
        'section_title': 'Historial de Transacciones'  # Add this line
    }
    return render(request, 'transacciones/lista_transacciones.html', context)

    # Limitar resultados para mejor rendimiento en móviles
    limit = int(request.GET.get('limit', 20))
    
    results = []
    for t in transacciones[:limit]:  # Usar el límite dinámico
        cliente_nombre = t.cliente.nombre if t.cliente else "Consumidor Final"
        results.append({
            'id': t.id,
            'fecha': t.fecha_hora.strftime('%d/%m/%Y %H:%M'),
            'cliente': cliente_nombre,
            'total': float(t.total),
            'metodo_pago': t.get_metodo_pago_display() if hasattr(t, 'get_metodo_pago_display') else t.metodo_pago,
        })
    
    return JsonResponse({
        'results': results,
        'total': transacciones.count(),
        'has_more': transacciones.count() > limit
    }, safe=False)


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
