from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import BusinessSettingsForm
from apps.usuarios.models import Business
from django.contrib.auth import update_session_auth_hash
from .models import BusinessConfiguration

# Add this new view function for the index page
@login_required
def index(request):
    """
    View for the configuration index page that lists all configuration options
    """
    return render(request, 'configuraciones/index.html')

# Add the JSON data function for reports
def obtener_empresa_json(request):
    """Devuelve los datos de la empresa en formato JSON para uso en reportes"""
    try:
        # Intentar obtener la configuración del negocio del usuario actual
        if request.user.is_authenticated:
            empresa = Business.objects.filter(user=request.user).first()
        else:
            # Si no hay usuario autenticado, intentar obtener cualquier configuración
            empresa = Business.objects.first()
            
        if empresa:
            data = {
                'nombre': empresa.nombre_negocio,
                'direccion': empresa.direccion_negocio or "Dirección no disponible",
                'telefono': empresa.telefono_negocio or "Teléfono no disponible",
                'logo_url': empresa.logo.url if empresa.logo else ""
            }
        else:
            raise Business.DoesNotExist
            
    except (Business.DoesNotExist, AttributeError):
        data = {
            'nombre': "Southern Food",
            'direccion': "Dirección no disponible",
            'telefono': "Teléfono no disponible",
            'logo_url': ""
        }
    
    return JsonResponse(data)

@login_required
def business_config(request):
    # Get or create business for the current user
    business, created = Business.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = BusinessSettingsForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            business = form.save(commit=False)
            business.user = request.user
            business.save()
            messages.success(request, "Configuración actualizada exitosamente.")
            return redirect('configuraciones:business_config')
    else:
        form = BusinessSettingsForm(instance=business)
    
    # Print debug info to console
    print(f"Business data: {business.nombre_negocio}, {business.direccion_negocio}")
    print(f"Form fields: {form.fields}")
    print(f"Form initial data: {form.initial}")
    
    return render(request, 'configuraciones/business_config.html', {
        'form': form,
        'business': business,
    })


@login_required
def personalizacion(request):
    """
    View for personalization settings
    """
    # Get current personalization settings
    business, created = Business.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Process personalization form
        primary_color = request.POST.get('primary_color')
        secondary_color = request.POST.get('secondary_color')
        default_view = request.POST.get('default_view')
        show_product_images = request.POST.get('show_product_images') == 'on'
        use_custom_brand_name = request.POST.get('use_custom_brand_name') == 'on'
        custom_brand_name = request.POST.get('custom_brand_name', '')[:12]
        dark_mode = request.POST.get('dark_mode') == 'true'
        use_custom_logo = request.POST.get('use_custom_logo') == 'on'
        custom_logo = request.FILES.get('custom_logo')
        
        # Validate color format
        if not primary_color.startswith('#') or len(primary_color) != 7:
            primary_color = '#10b981'  # Default emerald color
        if not secondary_color.startswith('#') or len(secondary_color) != 7:
            secondary_color = '#6366f1'  # Default indigo color
        
        # Handle logo upload
        if use_custom_logo and custom_logo:
            # Delete old logo if exists
            if business.logo:
                business.logo.delete()
            # Save new logo
            business.logo = custom_logo
        elif not use_custom_logo and business.logo:
            # Delete logo if checkbox is unchecked
            business.logo.delete()
            business.logo = None
        
        # Save to business settings
        business.primary_color = primary_color
        business.secondary_color = secondary_color
        business.default_view = default_view
        business.show_product_images = show_product_images
        business.use_custom_brand_name = use_custom_brand_name
        business.custom_brand_name = custom_brand_name
        business.dark_mode = dark_mode
        business.use_custom_logo = use_custom_logo
        business.save()
        
        messages.success(request, 'Configuración de personalización guardada correctamente.')
        return redirect('configuraciones:personalizacion')
    
    # Get current personalization settings
    context = {
        'primary_color': business.primary_color,
        'secondary_color': business.secondary_color,
        'default_view': business.default_view,
        'show_product_images': business.show_product_images,
        'use_custom_brand_name': business.use_custom_brand_name,
        'custom_brand_name': business.custom_brand_name,
        'dark_mode': business.dark_mode,
        'use_custom_logo': business.use_custom_logo,
        'custom_logo_url': business.logo.url if business.logo else None,
    }
    
    return render(request, 'configuraciones/personalizacion.html', context)

# Add these placeholder views after the personalizacion function

@login_required
def cuenta(request):
    """
    View for account settings
    """
    # Get user information
    user = request.user
    
    # Get business information
    business, created = Business.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Process form submission
        # Update user information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Update password if provided
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and confirm_password and new_password == confirm_password:
            user.set_password(new_password)
            # We'll need to re-login the user since changing password logs them out
            update_session_auth_hash(request, user)
        
        user.save()
        
        # Update business information
        business.nombre_negocio = request.POST.get('nombre_negocio', business.nombre_negocio)
        business.ruc_negocio = request.POST.get('ruc_negocio', business.ruc_negocio)
        business.direccion_negocio = request.POST.get('direccion_negocio', business.direccion_negocio)
        business.ciudad = request.POST.get('ciudad', business.ciudad)
        business.telefono_negocio = request.POST.get('telefono_negocio', business.telefono_negocio)
        business.email_negocio = request.POST.get('email_negocio', business.email_negocio)
        
        # Handle logo upload if provided
        if 'logo' in request.FILES:
            business.logo = request.FILES['logo']
            
        business.save()
        
        messages.success(request, "Información de cuenta actualizada exitosamente.")
        return redirect('configuraciones:cuenta')
    
    context = {
        'user': user,
        'business': business,
    }
    
    return render(request, 'configuraciones/cuenta.html', context)

@login_required
def usuarios(request):
    """
    View for user management settings
    """
    messages.info(request, "Esta sección está en desarrollo.")
    return render(request, 'configuraciones/usuarios.html', {})

@login_required
def sistema(request):
    """
    View for system settings
    """
    messages.info(request, "Esta sección está en desarrollo.")
    return render(request, 'configuraciones/sistema.html', {})


# Add this import at the top of the file
from django.http import JsonResponse
from .models import BusinessConfiguration

# Add this view function
def business_config_api(request):
    """API endpoint to get business configuration"""
    try:
        business_config = BusinessConfiguration.objects.first()
        if business_config:
            return JsonResponse({
                'nombre_negocio': business_config.nombre_negocio,
                'iva_porcentaje': business_config.iva_porcentaje,
                'moneda': business_config.moneda,
                'formato_fecha': business_config.formato_fecha,
            })
        else:
            return JsonResponse({
                'nombre_negocio': 'Mi Negocio',
                'iva_porcentaje': 12,
                'moneda': '$',
                'formato_fecha': 'd/m/Y',
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
