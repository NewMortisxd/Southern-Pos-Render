"""
Vistas para Kitchen Display System (KDS) y Pantalla Pública.
Separadas de views.py para mantener organización.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from functools import wraps
from apps.usuarios.models import Business
from .models import Order
from .services import OrderService


def ajax_login_required(view_func):
    """
    Decorador que verifica autenticación y devuelve JSON en lugar de redireccionar.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autenticado. Por favor, inicia sesión.'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def kds_view(request):
    """
    Vista para Kitchen Display System (KDS).
    Muestra pedidos activos (PENDING, PREPARING) en modo fullscreen.
    Solo accesible si el negocio tiene KDS habilitado.
    """
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return render(request, 'ventas/kds_error.html', {
            'error': 'No se encontró configuración de negocio'
        })
    
    # Verificar que el negocio tenga KDS habilitado
    if not business.enable_kds:
        return render(request, 'ventas/kds_error.html', {
            'error': 'KDS no está habilitado para este negocio'
        })
    
    # Verificar que el negocio soporte órdenes
    if not business.supports_orders():
        return render(request, 'ventas/kds_error.html', {
            'error': 'Este negocio no soporta sistema de órdenes'
        })
    
    # Obtener órdenes activas
    orders = OrderService.get_active_orders(business)
    
    context = {
        'orders': orders,
        'business': business,
        'current_time': timezone.now(),
    }
    
    return render(request, 'ventas/kds.html', context)


@ajax_login_required
def kds_orders_json(request):
    """
    API endpoint para obtener órdenes activas en formato JSON.
    Usado para polling desde el frontend.
    """
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return JsonResponse({'error': 'Negocio no encontrado'}, status=404)
    
    if not business.enable_kds or not business.supports_orders():
        return JsonResponse({'error': 'KDS no disponible'}, status=403)
    
    orders = OrderService.get_active_orders(business)
    
    orders_data = []
    for order in orders:
        items = []
        if order.sale.exists():
            sale = order.sale.first()
            for detalle in sale.detalleventa_set.all():
                items.append({
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                })
        
        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.isoformat(),
            'elapsed_time': order.get_elapsed_time(),
            'items': items,
            'notes': order.notes or '',
        })
    
    return JsonResponse({
        'orders': orders_data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@ajax_login_required
@require_POST
def kds_update_status(request, order_id):
    """
    Actualiza el estado de una orden desde el KDS.
    Acciones: Iniciar (PREPARING), Listo (READY), Cancelar (CANCELLED)
    """
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return JsonResponse({'error': 'Negocio no encontrado'}, status=404)
    
    if not business.enable_kds:
        return JsonResponse({'error': 'KDS no habilitado'}, status=403)
    
    # Obtener la orden y verificar que pertenece al negocio
    try:
        order = Order.objects.get(id=order_id, business=business)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Orden no encontrada'}, status=404)
    
    # Obtener el nuevo estado del request
    new_status = request.POST.get('status')
    
    if not new_status:
        return JsonResponse({'error': 'Estado no especificado'}, status=400)
    
    # Validar transiciones permitidas desde KDS
    allowed_transitions = {
        'PENDING': ['PREPARING', 'CANCELLED'],
        'PREPARING': ['READY', 'PENDING', 'CANCELLED'],  # Puede regresar a PENDING
        'READY': ['DELIVERED', 'PREPARING'],  # Puede regresar a PREPARING
    }
    
    if order.status not in allowed_transitions:
        return JsonResponse({
            'error': f'No se puede cambiar el estado desde {order.get_status_display()}'
        }, status=400)
    
    if new_status not in allowed_transitions[order.status]:
        return JsonResponse({
            'error': f'No se puede cambiar de {order.get_status_display()} a {dict(Order.STATUS_CHOICES).get(new_status, new_status)}'
        }, status=400)
    
    try:
        # Actualizar el estado usando el servicio
        updated_order = OrderService.update_order_status(order_id, new_status)
        
        return JsonResponse({
            'success': True,
            'order_id': updated_order.id,
            'order_number': updated_order.order_number,
            'status': updated_order.status,
            'status_display': updated_order.get_status_display(),
        })
    except Exception as e:
        import traceback
        print(f"Error updating order status: {traceback.format_exc()}")
        return JsonResponse({'error': f'Error al actualizar: {str(e)}'}, status=500)


@login_required
def public_display_view(request):
    """
    Vista para Pantalla Pública.
    Muestra únicamente pedidos con status=READY.
    Solo accesible si el negocio tiene pantalla pública habilitada.
    """
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return render(request, 'ventas/display_error.html', {
            'error': 'No se encontró configuración de negocio'
        })
    
    # Verificar que el negocio tenga pantalla pública habilitada
    if not business.enable_public_display:
        return render(request, 'ventas/display_error.html', {
            'error': 'Pantalla pública no está habilitada para este negocio'
        })
    
    # Verificar que el negocio soporte órdenes
    if not business.supports_orders():
        return render(request, 'ventas/display_error.html', {
            'error': 'Este negocio no soporta sistema de órdenes'
        })
    
    # Obtener órdenes listas
    orders = OrderService.get_ready_orders(business)
    
    context = {
        'orders': orders,
        'business': business,
        'current_time': timezone.now(),
    }
    
    return render(request, 'ventas/public_display.html', context)


@ajax_login_required
def display_orders_json(request):
    """
    API endpoint para obtener órdenes activas en formato JSON.
    Usado para polling desde el frontend de la pantalla pública.
    Devuelve órdenes en PREPARING y READY.
    """
    try:
        business = Business.objects.get(user=request.user)
    except Business.DoesNotExist:
        return JsonResponse({'error': 'Negocio no encontrado'}, status=404)
    
    if not business.enable_public_display or not business.supports_orders():
        return JsonResponse({'error': 'Pantalla pública no disponible'}, status=403)
    
    # Obtener órdenes en preparación y listas
    orders = Order.objects.filter(
        business=business,
        status__in=['PREPARING', 'READY']
    ).order_by('created_at')
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'ready_at': order.ready_at.isoformat() if order.ready_at else None,
        })
    
    return JsonResponse({
        'orders': orders_data,
        'timestamp': timezone.now().isoformat()
    })
