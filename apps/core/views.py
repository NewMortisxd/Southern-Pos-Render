from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json

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
    from decimal import Decimal
    from django.db.models import Q, F
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Obtener configuración del negocio
    try:
        business = Business.objects.get(user=request.user)
        modo_operacion = business.modo_operacion
        currency_symbol = business.moneda or '$'
    except Business.DoesNotExist:
        business = None
        modo_operacion = 'restaurante'
        currency_symbol = '$'

    # --- KPIs Inteligentes ---
    
    # Ventas de hoy
    ventas_hoy_total = Venta.objects.filter(
        transaccion__fecha__date=today,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Ventas de ayer para comparación
    ventas_ayer_total = Venta.objects.filter(
        transaccion__fecha__date=yesterday,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Calcular porcentaje de cambio
    if ventas_ayer_total > 0:
        cambio_ventas = ((ventas_hoy_total - ventas_ayer_total) / ventas_ayer_total) * 100
    else:
        cambio_ventas = 100 if ventas_hoy_total > 0 else 0
    
    # Facturas emitidas hoy
    facturas_hoy = Venta.objects.filter(
        transaccion__fecha__date=today,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).count()
    
    facturas_ayer = Venta.objects.filter(
        transaccion__fecha__date=yesterday,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).count()
    
    cambio_facturas = facturas_hoy - facturas_ayer
    
    # Productos vendidos hoy (unidades)
    productos_vendidos_hoy = DetalleVenta.objects.filter(
        venta__transaccion__fecha__date=today,
        venta__transaccion__procesado_pago=True,
        venta__transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    productos_vendidos_ayer = DetalleVenta.objects.filter(
        venta__transaccion__fecha__date=yesterday,
        venta__transaccion__procesado_pago=True,
        venta__transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    cambio_productos = productos_vendidos_hoy - productos_vendidos_ayer
    
    # Producto más vendido del día
    producto_top_hoy = DetalleVenta.objects.filter(
        venta__transaccion__fecha__date=today,
        venta__transaccion__procesado_pago=True,
        venta__transaccion__usuario_creador=request.user
    ).values('producto__nombre').annotate(
        total=Sum('cantidad')
    ).order_by('-total').first()
    
    # Nuevos clientes hoy
    clientes_nuevos_hoy = Cliente.objects.filter(
        fecha_registro__date=today,
        usuario_creador=request.user
    ).count()
    
    clientes_ayer = Cliente.objects.filter(
        fecha_registro__date=yesterday,
        usuario_creador=request.user
    ).count()
    
    # IVA generado hoy
    iva_hoy = Venta.objects.filter(
        transaccion__fecha__date=today,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('iva'))['total'] or Decimal('0')
    
    iva_ayer = Venta.objects.filter(
        transaccion__fecha__date=yesterday,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('iva'))['total'] or Decimal('0')
    
    # Calcular cambio de IVA
    if iva_ayer > 0:
        cambio_iva = ((iva_hoy - iva_ayer) / iva_ayer) * 100
    else:
        cambio_iva = 100 if iva_hoy > 0 else 0
    
    # IVA acumulado del mes
    primer_dia_mes = today.replace(day=1)
    iva_mes = Venta.objects.filter(
        transaccion__fecha__date__gte=primer_dia_mes,
        transaccion__fecha__date__lte=today,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).aggregate(total=Sum('iva'))['total'] or Decimal('0')
    
    # --- Ventas últimos 7 días para gráfico ---
    ventas_7_dias = []
    mejor_dia = {'fecha': '', 'total': 0}
    
    for i in range(6, -1, -1):
        fecha = today - timedelta(days=i)
        total = Venta.objects.filter(
            transaccion__fecha__date=fecha,
            transaccion__procesado_pago=True,
            transaccion__usuario_creador=request.user
        ).aggregate(total=Sum('total'))['total'] or 0
        
        ventas_7_dias.append({
            'fecha': fecha.strftime('%d/%m'),
            'total': float(total)
        })
        
        # Encontrar el mejor día
        if float(total) > mejor_dia['total']:
            mejor_dia = {
                'fecha': fecha.strftime('%A'),  # Nombre del día
                'total': float(total)
            }
    
    # Traducir día al español
    dias_es = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    mejor_dia['fecha'] = dias_es.get(mejor_dia['fecha'], mejor_dia['fecha'])
    
    # --- Productos más vendidos con ranking ---
    productos_top_raw = DetalleVenta.objects.filter(
        venta__transaccion__procesado_pago=True,
        venta__transaccion__usuario_creador=request.user,
        venta__transaccion__fecha__date__gte=week_ago
    ).values('producto__nombre', 'producto__precio').annotate(
        cantidad=Sum('cantidad'),
        ingresos=Sum('subtotal')
    ).order_by('-ingresos')[:5]
    
    # Convertir a lista y agregar ranking + participación
    productos_top = []
    total_ingresos = sum(p['ingresos'] for p in productos_top_raw) or 1
    for idx, producto in enumerate(productos_top_raw, 1):
        producto['ranking'] = idx
        producto['participacion'] = (float(producto['ingresos']) / float(total_ingresos)) * 100
        productos_top.append(producto)
    
    # --- Métodos de pago con porcentajes ---
    metodos_pago_raw = Venta.objects.filter(
        transaccion__fecha__date__gte=week_ago,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).values('metodo_pago').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    )
    
    # Calcular porcentajes
    metodos_pago = list(metodos_pago_raw)
    total_metodos = sum(m['total'] for m in metodos_pago) or 1
    for metodo in metodos_pago:
        metodo['porcentaje'] = (float(metodo['total']) / float(total_metodos)) * 100
    
    # --- Promedio últimos 7 días ---
    promedio_7_dias = Venta.objects.filter(
        transaccion__fecha__date__gte=week_ago,
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).aggregate(promedio=Sum('total'))['promedio'] or Decimal('0')
    
    if promedio_7_dias > 0:
        promedio_7_dias = promedio_7_dias / 7
    
    # --- Ticket promedio (MOVER AQUÍ ANTES DE LAS ALERTAS) ---
    if facturas_hoy > 0:
        ticket_promedio = ventas_hoy_total / facturas_hoy
    else:
        ticket_promedio = Decimal('0')
    
    # Ticket promedio de ayer
    if facturas_ayer > 0:
        ticket_promedio_ayer = ventas_ayer_total / facturas_ayer
    else:
        ticket_promedio_ayer = Decimal('0')
    
    # Calcular cambio de ticket promedio
    if ticket_promedio_ayer > 0:
        cambio_ticket = ((ticket_promedio - ticket_promedio_ayer) / ticket_promedio_ayer) * 100
    else:
        cambio_ticket = 100 if ticket_promedio > 0 else 0
    
    # --- Ventas recientes con contexto temporal ---
    ventas_recientes = Venta.objects.filter(
        transaccion__procesado_pago=True,
        transaccion__usuario_creador=request.user
    ).select_related('cliente').prefetch_related('transaccion_set').order_by('-fecha_hora')[:10]
    
    # Agrupar por fecha
    ventas_agrupadas = {}
    for venta in ventas_recientes:
        fecha_venta = venta.fecha_hora.date()
        if fecha_venta == today:
            grupo = 'Hoy'
        elif fecha_venta == yesterday:
            grupo = 'Ayer'
        else:
            grupo = fecha_venta.strftime('%d/%m/%Y')
        
        if grupo not in ventas_agrupadas:
            ventas_agrupadas[grupo] = {
                'ventas': [],
                'total': Decimal('0'),
                'cantidad': 0
            }
        ventas_agrupadas[grupo]['ventas'].append(venta)
        ventas_agrupadas[grupo]['total'] += venta.total
        ventas_agrupadas[grupo]['cantidad'] += 1
    
    # Última venta
    ultima_venta = ventas_recientes.first() if ventas_recientes else None
    
    # --- Alertas inteligentes predictivas ---
    alertas = []
    
    # Alerta: productos con bajo stock
    productos_bajo_stock = Producto.objects.filter(
        usuario_creador=request.user,
        stock__lte=5,
        stock__gt=0
    ).count()
    if productos_bajo_stock > 0:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'{productos_bajo_stock} producto(s) con bajo stock'
        })
    
    # Alerta predictiva: ventas muy bajas vs promedio
    if ventas_hoy_total > 0 and promedio_7_dias > 0:
        diferencia_promedio = ((ventas_hoy_total - promedio_7_dias) / promedio_7_dias) * 100
        if diferencia_promedio < -30:
            alertas.append({
                'tipo': 'danger',
                'mensaje': f'Ventas {abs(diferencia_promedio):.0f}% menores que promedio semanal'
            })
    
    # Alerta: ticket promedio bajando
    if ticket_promedio > 0 and cambio_ticket < -10:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'Ticket promedio bajó {abs(cambio_ticket):.0f}% vs ayer'
        })
    
    # Alerta: alta dependencia de efectivo
    total_efectivo = sum(m['total'] for m in metodos_pago if m['metodo_pago'] == 'cash') or 0
    total_metodos = sum(m['total'] for m in metodos_pago) or 1
    porcentaje_efectivo = (float(total_efectivo) / float(total_metodos)) * 100
    if porcentaje_efectivo > 80 and total_metodos > 0:
        alertas.append({
            'tipo': 'info',
            'mensaje': f'Alta dependencia de efectivo ({porcentaje_efectivo:.0f}%)'
        })
    
    # Alerta: sin ventas hoy
    if ventas_hoy_total == 0 and ultima_venta:
        tiempo_desde_ultima = timezone.now() - ultima_venta.fecha_hora
        if tiempo_desde_ultima.days == 0:
            horas = tiempo_desde_ultima.seconds // 3600
            alertas.append({
                'tipo': 'info',
                'mensaje': f'Sin ventas hoy. Última venta hace {horas}h'
            })
        else:
            alertas.append({
                'tipo': 'info',
                'mensaje': f'Sin ventas hoy. Última venta: {ultima_venta.fecha_hora.strftime("%d/%m/%Y %H:%M")}'
            })
    
    # --- Mensaje motivacional dinámico ---
    mensaje_motivacional = None
    if ventas_hoy_total > 0 and promedio_7_dias > 0:
        diferencia_promedio = ((ventas_hoy_total - promedio_7_dias) / promedio_7_dias) * 100
        if diferencia_promedio > 15:
            mensaje_motivacional = {
                'tipo': 'success',
                'icono': 'trending-up',
                'texto': f'¡Excelente trabajo! Ventas hoy {diferencia_promedio:.0f}% superiores al promedio semanal'
            }
        elif diferencia_promedio < -15:
            mensaje_motivacional = {
                'tipo': 'warning',
                'icono': 'alert-triangle',
                'texto': f'Ventas hoy {abs(diferencia_promedio):.0f}% por debajo del promedio. Revisa estrategias'
            }
    elif ventas_hoy_total == 0 and facturas_hoy == 0:
        hora_actual = timezone.now().hour
        if hora_actual < 12:
            mensaje_motivacional = {
                'tipo': 'info',
                'icono': 'sunrise',
                'texto': 'Buenos días. Aún no hay ventas registradas hoy'
            }
        elif hora_actual < 18:
            mensaje_motivacional = {
                'tipo': 'info',
                'icono': 'sun',
                'texto': 'Sin ventas aún. Promedio esperado: ' + f'{currency_symbol}{promedio_7_dias:.2f}'
            }
        else:
            mensaje_motivacional = {
                'tipo': 'warning',
                'icono': 'moon',
                'texto': 'Sin ventas hoy. Revisa operaciones del negocio'
            }

    # --- Datos para el panel de control del usuario ---
    context = {
        # KPIs principales
        'ventas_hoy_pagadas_total': ventas_hoy_total,
        'cambio_ventas': cambio_ventas,
        'facturas_hoy': facturas_hoy,
        'cambio_facturas': cambio_facturas,
        'productos_vendidos_hoy': productos_vendidos_hoy,
        'cambio_productos': cambio_productos,
        'producto_top_hoy': producto_top_hoy,
        'clientes_nuevos_count': clientes_nuevos_hoy,
        'iva_hoy': iva_hoy,
        'cambio_iva': cambio_iva,
        'iva_mes': iva_mes,
        'ticket_promedio': ticket_promedio,
        'cambio_ticket': cambio_ticket,
        'mensaje_motivacional': mensaje_motivacional,
        
        # Gráficos
        'ventas_7_dias': json.dumps(ventas_7_dias),
        'mejor_dia': mejor_dia,
        'productos_mas_vendidos_pagados': productos_top,
        'metodos_pago': metodos_pago,
        'promedio_7_dias': promedio_7_dias,
        
        # Ventas recientes
        'ventas_recientes_pagadas': ventas_recientes,
        'ventas_agrupadas': ventas_agrupadas,
        'ultima_venta': ultima_venta,
        
        # Alertas
        'alertas': alertas,
        
        # Configuración
        'modo_operacion': modo_operacion,
        'business': business,
        'currency_symbol': '$',  # Símbolo de moneda
        
        # Legacy (mantener compatibilidad)
        'ordenes_hoy_pagadas_count': facturas_hoy,
        'productos_nuevos_count': Producto.objects.filter(
            fecha_creacion__date=today,
            usuario_creador=request.user
        ).count(),
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
            business.ciudad = request.POST.get('ciudad', '')  # Nuevo campo
            business.telefono_negocio = request.POST.get('telefono_negocio', '')
            business.email_negocio = request.POST.get('email_negocio', '')
            business.plan = request.POST.get('plan', 'free')  # Guardar plan seleccionado

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
