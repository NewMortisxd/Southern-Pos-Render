def business_settings(request):
    """
    Inyecta configuración empresarial personalizable en todos los templates:
    - Moneda, colores y marca para white-labeling
    - Modo oscuro según preferencia del negocio
    - Valores por defecto robustos para evitar errores en templates
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            business = request.user.business  # Accede a la relación OneToOne
            
            # Configuración monetaria (crítica para reportes fiscales)
            context['currency_symbol'] = business.moneda  # Símbolo personalizado
            
            # Tema visual (RGB usado para manipulaciones JS/CSS dinámicas)
            context['theme_settings'] = {
                'primary_color': business.primary_color,
                'primary_color_rgb': business.primary_color.lstrip('#'),  # Formato para CSS rgba()
                'secondary_color': business.secondary_color,
                'secondary_color_rgb': business.secondary_color.lstrip('#'),
            }
            
            # Preferencia de UI (persistente en sesión)
            context['dark_mode'] = business.dark_mode
            
            # White-labeling (marca visible en facturas/PDFs)
            context['brand_name'] = (
                business.custom_brand_name 
                if business.use_custom_brand_name and business.custom_brand_name
                else 'SouthernPOS'  # Valor por defecto registrado
            )
                
        except Exception:  # Broad exception para evitar 500 en cualquier fallo
            # Fallback seguro cuando no existe configuración
            context.update({
                'currency_symbol': '$',  # USD como default
                'theme_settings': {
                    'primary_color': '#10b981',  # Verde esmeralda
                    'primary_color_rgb': '16, 185, 129',
                    'secondary_color': '#6366f1',  # Índigo
                    'secondary_color_rgb': '99, 102, 241',
                },
                'dark_mode': False,
                'brand_name': 'SouthernPOS'  # Marca base
            })
    
    return context