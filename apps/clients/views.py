from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente
from .forms import ClienteForm
from django.http import JsonResponse
from django.db.models import Q

# Vista para buscar clientes mediante AJAX
def search_clients(request):
    """
    Busca clientes por nombre, identificación o código.
    Devuelve una respuesta JSON con los clientes coincidentes.
    """
    term = request.GET.get('term', '')
    
    if len(term) < 2:
        return JsonResponse({'results': []})
    
    # Busca clientes que coincidan con el término y pertenezcan al usuario actual
    clients = Cliente.objects.filter(
        Q(nombre__icontains=term) | 
        Q(identificacion__icontains=term) |
        Q(codigo__icontains=term)
    ).filter(estado=True, usuario_creador=request.user)[:10]  # Limita a 10 resultados
    
    # Formatea los resultados
    results = []
    for client in clients:
        results.append({
            'id': client.id,
            'codigo': client.codigo,
            'nombre': client.nombre,
            'identificacion': client.identificacion,
            'direccion': client.direccion,
            'ciudad': client.ciudad
        })
    
    return JsonResponse({'results': results})

# Vista para listar clientes
def lista_clientes(request):
    # Obtiene parámetros de consulta
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'nombre')
    estado_filter = request.GET.get('estado', '')
    
    # Filtra clientes por el usuario actual
    clientes = Cliente.objects.filter(usuario_creador=request.user)
    
    # Aplica filtro de búsqueda si se proporciona
    if query:
        clientes = clientes.filter(
            nombre__icontains=query
        ) | clientes.filter(
            identificacion__icontains=query
        ) | clientes.filter(
            email__icontains=query
        )
    
    # Aplica filtro por estado si se proporciona
    if estado_filter:
        clientes = clientes.filter(estado=estado_filter)
    
    # Aplica ordenación
    if sort_by == 'identificacion':
        clientes = clientes.order_by('identificacion')
    elif sort_by == 'email':
        clientes = clientes.order_by('email')
    elif sort_by == 'grupo':
        clientes = clientes.order_by('grupo')
    elif sort_by == 'estado':
        clientes = clientes.order_by('estado')
    else:
        clientes = clientes.order_by('nombre')
    
    context = {
        'clientes': clientes,
        'query': query,
        'sort_by': sort_by,
        'estado_filter': estado_filter,
        'section_title': 'Lista de Clientes'
    }
    
    return render(request, 'clients/lista_clientes.html', context)

# Vista para agregar un nuevo cliente
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            # Guarda sin confirmar en la base de datos aún
            cliente = form.save(commit=False)
            # Asocia el cliente con el usuario actual
            cliente.usuario_creador = request.user
            cliente.save()
            messages.success(request, 'Cliente agregado correctamente.')
            return redirect('clients:lista')
        else:
            # Imprime errores del formulario si los hay
            print("Form errors:", form.errors)
    else:
        form = ClienteForm()
    
    return render(request, 'clients/form_cliente.html', {
        'form': form,
        'section_title': 'Agregar Cliente'
    })

# Vista para editar un cliente existente
def editar_cliente(request, cliente_id):
    # Solo permite editar clientes creados por el usuario actual
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario_creador=request.user)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            # Imprime los datos del formulario para verificar
            print("Form data:", form.cleaned_data)
            cliente = form.save()
            # Imprime el cliente guardado para verificar el campo comentarios
            print("Saved cliente:", cliente.comentarios)
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('clients:lista')
        else:
            # Imprime errores del formulario si los hay
            print("Form errors:", form.errors)
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'clients/form_cliente.html', {
        'form': form,
        'cliente': cliente,
        'section_title': 'Editar Cliente'
    })

# Vista para eliminar un cliente
def eliminar_cliente(request, cliente_id):
    # Solo permite eliminar clientes creados por el usuario actual
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario_creador=request.user)
    
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('clients:lista')
    
    return render(request, 'clients/eliminar_cliente.html', {
        'cliente': cliente,
        'section_title': 'Eliminar Cliente'
    })

# Vista para ver los detalles de un cliente
def detalle_cliente(request, cliente_id):
    # Solo permite ver clientes creados por el usuario actual
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario_creador=request.user)
    
    return render(request, 'clients/detalle_cliente.html', {
        'cliente': cliente,
        'section_title': 'Detalle de Cliente'
    })

# Vista para búsqueda de clientes mediante AJAX
def client_search_view(request):
    """
    Maneja solicitudes de búsqueda AJAX para clientes.
    """
    search_term = request.GET.get('q', '')
    
    if search_term:
        # Filtra por el usuario actual
        clients = Cliente.objects.filter(
            Q(nombre__icontains=search_term) | 
            Q(identificacion__icontains=search_term),
            usuario_creador=request.user
        ).values('id', 'nombre', 'identificacion', 'direccion', 'ciudad', 'codigo')
        
        return JsonResponse(list(clients), safe=False)
    
    return JsonResponse([], safe=False)