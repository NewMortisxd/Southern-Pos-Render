from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

# Importa formularios y modelos necesarios de tus apps personalizadas
from apps.usuarios.forms import RegistrationForm
from apps.ventas.models import Venta, DetalleVenta
from apps.clients.models import Cliente
from apps.productos.models import Producto
from apps.transacciones.models import Transaccion
from apps.usuarios.models import Business  # Modelo de información del negocio asociado al usuario

# Vista de inicio de sesión personalizada
def login_view(request):
    if request.method == 'POST':
        # Autenticación del usuario con credenciales enviadas
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Inicia sesión y redirige al dashboard
            login(request, user)
            return redirect('dashboard')
        else:
            # Muestra mensaje de error si las credenciales no son válidas
            return render(request, 'usuarios/login.html', {
                'error': 'Credenciales inválidas. Por favor intente de nuevo.'
            })
    
    # Renderiza el formulario vacío de login
    return render(request, 'usuarios/login.html')

# Vista principal del sistema, solo accesible para usuarios autenticados
@login_required
def dashboard(request):
    today = timezone.now().date()

    # --- Datos para el panel de control del usuario ---
    context = {
        # Total en ventas pagadas del día actual
        'ventas_hoy_pagadas_total': Venta.objects.filter(
            transaccion__fecha__date=today,
            transaccion__procesado_pago=True,
            transaccion__usuario_creador=request.user
        ).aggregate(total=Sum('total'))['total'] or 0,

        # Cantidad de órdenes pagadas hoy
        'ordenes_hoy_pagadas_count': Venta.objects.filter(
            transaccion__fecha__date=today,
            transaccion__procesado_pago=True,
            transaccion__usuario_creador=request.user
        ).count(),

        # Nuevos clientes registrados hoy por este usuario
        'clientes_nuevos_count': Cliente.objects.filter(
            fecha_registro__date=today,
            usuario_creador=request.user
        ).count(),

        # Nuevos productos creados hoy por este usuario
        'productos_nuevos_count': Producto.objects.filter(
            fecha_creacion__date=today,
            usuario_creador=request.user
        ).count(),

        # Número de productos distintos vendidos en ventas pagadas hoy
        'productos_vendidos_pagados_count': DetalleVenta.objects.filter(
            venta__transaccion__fecha__date=today,
            venta__transaccion__procesado_pago=True,
            venta__transaccion__usuario_creador=request.user
        ).values('producto').distinct().count(),

        # Últimas 10 ventas pagadas hechas por el usuario
        'ventas_recientes_pagadas': Venta.objects.filter(
            transaccion__procesado_pago=True,
            transaccion__usuario_creador=request.user
        ).order_by('-fecha_hora')[:10],

        # Top 5 productos más vendidos en ventas pagadas del usuario
        'productos_mas_vendidos_pagados': Producto.objects.filter(
            detalleventa__venta__transaccion__procesado_pago=True,
            detalleventa__venta__transaccion__usuario_creador=request.user
        ).annotate(
            cantidad_vendida_pagada=Count('detalleventa')
        ).order_by('-cantidad_vendida_pagada')[:5]
    }

    return render(request, 'dashboard.html', context)

# Vista de registro de usuarios
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Crea el usuario pero aún no lo guarda
            user = form.save(commit=False)

            # Si no se proporcionó un nombre de usuario, usa el email
            if not user.username:
                user.username = user.email

            user.save()        # Guarda el usuario
            form.save_m2m()    # Guarda relaciones many-to-many, si las hay

            # Crea o recupera la información de negocio asociada al usuario
            business, created = Business.objects.get_or_create(user=user)

            # Extrae datos de negocio del formulario
            business.nombre_negocio = request.POST.get('nombre_negocio', '')
            business.ruc_negocio = request.POST.get('ruc_negocio', '')
            business.direccion_negocio = request.POST.get('direccion_negocio', '')
            business.ciudad = request.POST.get('ciudad', '')
            business.telefono_negocio = request.POST.get('telefono_negocio', '')
            business.email_negocio = request.POST.get('email_negocio', '')

            # Guarda el logo si fue proporcionado
            if 'logo' in request.FILES:
                business.logo = request.FILES['logo']

            business.save()

            # Inicia sesión automáticamente tras el registro
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'usuarios/register.html', {'form': form})
