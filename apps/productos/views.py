from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto, Categoria
from .models_config import ProductDisplayConfig, SavedProductFilter
from .forms import ProductoForm, CategoriaForm
from django.views.generic import CreateView
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

# ... (el resto de tu código permanece igual) ...

# Vista para listar categorías
@login_required
def lista_categorias(request):
    categorias = Categoria.objects.filter(usuario_creador=request.user)
    return render(request, 'productos/lista_categorias.html', {
        'categorias': categorias,
        'section_title': 'Categorías'
    })

# Vista para crear una nueva categoría
@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            # Asocia la categoría con el usuario actual
            categoria.usuario_creador = request.user
            categoria.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('productos:lista_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'productos/categoria_form.html', {
        'form': form,
        'section_title': 'Nueva Categoría'
    })

# Vista para editar una categoría
@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario_creador=request.user)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('productos:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'productos/categoria_form.html', {
        'form': form,
        'object': categoria,
        'section_title': 'Editar Categoría'
    })

# Vista para eliminar una categoría
@login_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario_creador=request.user)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente')
    return redirect('productos:lista_categorias')

# Vista genérica para crear una categoría
class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'productos/categoria_form.html'
    
    def form_valid(self, form):
        # Asocia la categoría con el usuario actual
        form.instance.usuario_creador = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('productos:lista')

# Vista para listar productos con configuración adaptable
@login_required
def lista_productos(request):
    # Obtener configuración de visualización del usuario
    config = ProductDisplayConfig.get_or_create_for_user(request.user)
    
    # Obtener vista actual (puede ser override por parámetro GET)
    vista_actual = request.GET.get('vista', config.vista_predeterminada)
    
    # Si el usuario cambia de vista manualmente, guardar su preferencia
    if 'vista' in request.GET and request.GET.get('vista') != config.vista_predeterminada:
        # Solo guardar si es diferente y es una vista válida
        vistas_validas = ['grid', 'list', 'table']
        if vista_actual in vistas_validas:
            config.vista_predeterminada = vista_actual
            config.save()
    
    # Obtener y guardar tamaño de grid si se especifica
    if 'tamano' in request.GET:
        tamano = request.GET.get('tamano')
        tamanos_validos = ['small', 'medium', 'large']
        if tamano in tamanos_validos and tamano != config.tamano_imagen_grid:
            config.tamano_imagen_grid = tamano
            config.save()
    
    # Obtener orden actual
    orden_actual = request.GET.get('orden', config.orden_predeterminado)
    
    # Si el usuario cambia el orden manualmente, guardar su preferencia
    if 'orden' in request.GET and request.GET.get('orden') != config.orden_predeterminado:
        ordenes_validos = [choice[0] for choice in ProductDisplayConfig.ORDEN_CHOICES]
        if orden_actual in ordenes_validos:
            config.orden_predeterminado = orden_actual
            config.save()
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    stock_bajo = request.GET.get('stock_bajo')
    sin_imagen = request.GET.get('sin_imagen')
    
    # Query base
    productos = Producto.objects.filter(
        usuario_creador=request.user
    ).select_related('categoria')
    
    # Aplicar filtros
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if stock_bajo:
        productos = productos.filter(stock__lte=config.umbral_stock_bajo)
    
    if sin_imagen:
        productos = productos.filter(imagen__isnull=True)
    
    # Aplicar orden
    productos = productos.order_by(orden_actual)
    
    # Paginación
    paginator = Paginator(productos, config.productos_por_pagina)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Obtener categorías para filtros
    categorias = Categoria.objects.filter(usuario_creador=request.user)
    
    # Obtener filtros guardados
    filtros_guardados = SavedProductFilter.objects.filter(user=request.user)
    
    context = {
        'productos': page_obj,
        'page_obj': page_obj,
        'config': config,
        'vista_actual': vista_actual,
        'orden_actual': orden_actual,
        'categorias': categorias,
        'filtros_guardados': filtros_guardados,
        'section_title': 'Productos',
        'total_productos': productos.count(),
    }
    
    return render(request, 'productos/lista_productos.html', context)

# Vista para crear un nuevo producto
@login_required
def crear_producto(request):
    # Obtener el modo de operación del negocio
    from apps.usuarios.models import Business
    try:
        business = Business.objects.get(user=request.user)
        modo_operacion = business.modo_operacion
    except Business.DoesNotExist:
        modo_operacion = 'restaurante'  # Valor por defecto
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            producto = form.save(commit=False)
            # Asegura que el producto esté asociado con el usuario actual
            producto.usuario_creador = request.user
            
            producto.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('productos:lista')
        else:
            messages.error(request, 'Error al crear el producto: ' + ', '.join(form.errors.get('imagen', [])))
    else:
        form = ProductoForm(user=request.user)
    return render(request, 'productos/form_producto.html', {
        'form': form,
        'section_title': 'Nuevo Producto',
        'modo_operacion': modo_operacion
    })

# Vista para editar un producto existente
@login_required
def editar_producto(request, pk):
    # Obtener el modo de operación del negocio
    from apps.usuarios.models import Business
    try:
        business = Business.objects.get(user=request.user)
        modo_operacion = business.modo_operacion
    except Business.DoesNotExist:
        modo_operacion = 'restaurante'  # Valor por defecto
    
    # Obtiene el producto solo si fue creado por el usuario actual
    producto = get_object_or_404(Producto, pk=pk, usuario_creador=request.user)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('productos:lista')
    else:
        form = ProductoForm(instance=producto, user=request.user)
    return render(request, 'productos/form_producto.html', {
        'form': form,
        'object': producto,
        'section_title': 'Editar Producto',
        'modo_operacion': modo_operacion
    })

# Vista para eliminar un producto
@login_required
def eliminar_producto(request, pk):
    # Solo permite eliminar productos creados por el usuario actual
    producto = get_object_or_404(Producto, pk=pk, usuario_creador=request.user)
    if request.method == 'POST':
        producto.delete()
    return redirect('productos:lista')



@login_required
def buscar_productos(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        productos = Producto.objects.filter(
            usuario_creador=request.user
        ).select_related('categoria')
        return render(request, 'productos/lista_productos.html', {
            'productos': productos,
            'section_title': 'Todos los productos',
            'query': query
        })
    
    # Buscar por código de barras exacto primero
    producto_por_codigo = Producto.objects.filter(
        usuario_creador=request.user,
        codigo_barras__iexact=query
    ).first()
    
    if producto_por_codigo:
        return render(request, 'productos/lista_productos.html', {
            'productos': [producto_por_codigo],
            'section_title': 'Resultados de búsqueda',
            'query': query
        })
    
    # Si no encuentra por código, buscar por nombre o descripción
    productos = Producto.objects.filter(
        usuario_creador=request.user
    ).filter(
        Q(nombre__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(codigo_barras__icontains=query)
    ).select_related('categoria')
    
    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'section_title': 'Resultados de búsqueda',
        'query': query
    })

@login_required
def buscar_producto_por_codigo(request):
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({'success': False, 'message': 'Código no proporcionado'}, status=400)
    
    try:
        producto = Producto.objects.get(
            codigo_barras=codigo,
            usuario_creador=request.user
        )
        data = {
            'success': True,
            'producto': {
                'id': producto.id,
                'codigo_barras': producto.codigo_barras,  # Campo correcto
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': producto.stock,
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                'imagen': producto.imagen.url if producto.imagen else None
            }
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Vista para actualizar configuración de visualización
@login_required
def actualizar_config_vista(request):
    """Actualiza la configuración de visualización vía AJAX"""
    if request.method == 'POST':
        config = ProductDisplayConfig.get_or_create_for_user(request.user)
        
        # Actualizar campos según lo enviado
        campo = request.POST.get('campo')
        valor = request.POST.get('valor')
        
        if campo and hasattr(config, campo):
            # Convertir valor según el tipo de campo
            if isinstance(getattr(config, campo), bool):
                valor = valor.lower() in ['true', '1', 'yes']
            elif isinstance(getattr(config, campo), int):
                valor = int(valor)
            
            setattr(config, campo, valor)
            config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración actualizada'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=400)


@login_required
def guardar_filtro(request):
    """Guarda un filtro personalizado"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        icono = request.POST.get('icono', 'filter')
        color = request.POST.get('color', 'emerald')
        
        filtros = {
            'categoria': request.POST.get('categoria'),
            'stock_bajo': request.POST.get('stock_bajo'),
            'sin_imagen': request.POST.get('sin_imagen'),
            'orden': request.POST.get('orden'),
            'vista': request.POST.get('vista'),
        }
        
        # Configuración de vista específica (opcional)
        config_vista = {}
        if request.POST.get('guardar_config_vista') == 'true':
            config = ProductDisplayConfig.get_or_create_for_user(request.user)
            config_vista = {
                'mostrar_imagenes': config.mostrar_imagenes,
                'mostrar_codigo_barras': config.mostrar_codigo_barras,
                'mostrar_stock': config.mostrar_stock,
                'mostrar_categoria': config.mostrar_categoria,
                'tamano_imagen_grid': config.tamano_imagen_grid,
            }
        
        try:
            filtro = SavedProductFilter.objects.create(
                user=request.user,
                nombre=nombre,
                descripcion=descripcion,
                filtros=filtros,
                config_vista=config_vista,
                icono=icono,
                color=color
            )
            
            return JsonResponse({
                'success': True,
                'filtro_id': filtro.id,
                'message': 'Vista guardada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=400)


@login_required
def aplicar_filtro_guardado(request, filtro_id):
    """Aplica un filtro guardado"""
    filtro = get_object_or_404(SavedProductFilter, id=filtro_id, user=request.user)
    
    # Incrementar contador de uso
    filtro.incrementar_uso()
    
    # Construir URL con los parámetros del filtro
    params = []
    for key, value in filtro.filtros.items():
        if value:
            params.append(f"{key}={value}")
    
    url = reverse('productos:lista')
    if params:
        url += '?' + '&'.join(params)
    
    return redirect(url)


@login_required
def eliminar_filtro_guardado(request, filtro_id):
    """Elimina un filtro guardado"""
    if request.method == 'POST':
        filtro = get_object_or_404(SavedProductFilter, id=filtro_id, user=request.user)
        nombre = filtro.nombre
        filtro.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Vista "{nombre}" eliminada'
            })
        
        messages.success(request, f'Vista "{nombre}" eliminada exitosamente')
        return redirect('productos:gestionar_vistas')
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=400)


@login_required
def gestionar_vistas(request):
    """Vista para gestionar todas las vistas guardadas"""
    vistas = SavedProductFilter.objects.filter(user=request.user).order_by('-es_favorito', '-veces_usado')
    
    return render(request, 'productos/gestionar_vistas.html', {
        'vistas': vistas,
        'section_title': 'Gestionar Vistas'
    })


@login_required
def editar_filtro_guardado(request, filtro_id):
    """Edita un filtro guardado"""
    filtro = get_object_or_404(SavedProductFilter, id=filtro_id, user=request.user)
    
    if request.method == 'POST':
        filtro.nombre = request.POST.get('nombre', filtro.nombre)
        filtro.descripcion = request.POST.get('descripcion', filtro.descripcion)
        filtro.icono = request.POST.get('icono', filtro.icono)
        filtro.color = request.POST.get('color', filtro.color)
        filtro.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Vista actualizada'
            })
        
        messages.success(request, 'Vista actualizada exitosamente')
        return redirect('productos:gestionar_vistas')
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=400)


@login_required
def toggle_favorito_filtro(request, filtro_id):
    """Marca/desmarca un filtro como favorito"""
    if request.method == 'POST':
        filtro = get_object_or_404(SavedProductFilter, id=filtro_id, user=request.user)
        filtro.es_favorito = not filtro.es_favorito
        filtro.save()
        
        return JsonResponse({
            'success': True,
            'es_favorito': filtro.es_favorito
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=400)


@login_required
def aplicar_preset(request, preset):
    """Aplica un preset de configuración (restaurante o retail)"""
    config = ProductDisplayConfig.get_or_create_for_user(request.user)
    
    if preset == 'restaurante':
        config.aplicar_preset_restaurante()
        messages.success(request, '✅ Configuración optimizada para Restaurante aplicada')
    elif preset == 'retail':
        config.aplicar_preset_retail()
        messages.success(request, '✅ Configuración optimizada para Retail aplicada')
    else:
        messages.error(request, 'Preset no válido')
    
    return redirect('productos:lista')


@login_required
def config_productos(request):
    """Vista para configurar la visualización de productos"""
    config = ProductDisplayConfig.get_or_create_for_user(request.user)
    
    if request.method == 'POST':
        # Actualizar configuración
        config.vista_predeterminada = request.POST.get('vista_predeterminada', config.vista_predeterminada)
        config.orden_predeterminado = request.POST.get('orden_predeterminado', config.orden_predeterminado)
        config.mostrar_imagenes = request.POST.get('mostrar_imagenes') == 'on'
        config.mostrar_codigo_barras = request.POST.get('mostrar_codigo_barras') == 'on'
        config.mostrar_stock = request.POST.get('mostrar_stock') == 'on'
        config.mostrar_categoria = request.POST.get('mostrar_categoria') == 'on'
        config.mostrar_descripcion = request.POST.get('mostrar_descripcion') == 'on'
        config.tamano_imagen_grid = request.POST.get('tamano_imagen_grid', config.tamano_imagen_grid)
        config.filtros_avanzados_activos = request.POST.get('filtros_avanzados_activos') == 'on'
        config.busqueda_codigo_barras_prioritaria = request.POST.get('busqueda_codigo_barras_prioritaria') == 'on'
        config.alerta_stock_bajo = request.POST.get('alerta_stock_bajo') == 'on'
        
        # Validar y convertir valores numéricos
        try:
            umbral = int(request.POST.get('umbral_stock_bajo', config.umbral_stock_bajo))
            config.umbral_stock_bajo = max(0, umbral)  # No permitir negativos
        except (ValueError, TypeError):
            pass  # Mantener valor actual si hay error
        
        try:
            productos_pagina = int(request.POST.get('productos_por_pagina', config.productos_por_pagina))
            config.productos_por_pagina = max(1, min(100, productos_pagina))  # Entre 1 y 100
        except (ValueError, TypeError):
            pass  # Mantener valor actual si hay error
        
        config.auto_configurar_por_modo = request.POST.get('auto_configurar_por_modo') == 'on'
        
        config.save()
        messages.success(request, '✅ Configuración guardada exitosamente')
        return redirect('productos:lista')
    
    return render(request, 'productos/config_productos.html', {
        'config': config,
        'section_title': 'Configuración de Productos'
    })
