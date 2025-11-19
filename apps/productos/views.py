from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse  # Asegúrate de tener esta importación
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm
from django.views.generic import CreateView
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # ¡ESTA ES LA IMPORTACIÓN QUE FALTABA!

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

# Vista para listar productos
@login_required
def lista_productos(request):
    # Filtra productos para mostrar solo los creados por el usuario actual
    productos = Producto.objects.filter(
        usuario_creador=request.user
    ).select_related('categoria')
    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'section_title': 'Productos'  
    })

# Vista para crear un nuevo producto
@login_required
def crear_producto(request):
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
        'section_title': 'Nuevo Producto'
    })

# Vista para editar un producto existente
@login_required
def editar_producto(request, pk):
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
        'section_title': 'Editar Producto'
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
