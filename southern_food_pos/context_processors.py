def business_settings(request):
    """
    Context processor to add business settings to all templates
    """
    if request.user.is_authenticated:
        from apps.usuarios.models import Business
        business, created = Business.objects.get_or_create(user=request.user)
        return {
            'business_settings': business
        }
    return {}


def theme_settings(request):
    """
    Context processor to add theme settings to all templates
    """
    if request.user.is_authenticated:
        from apps.usuarios.models import Business
        try:
            business = Business.objects.get(user=request.user)
            
            # Convert hex to RGB for CSS variables
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            primary_rgb = hex_to_rgb(business.primary_color)
            secondary_rgb = hex_to_rgb(business.secondary_color)
            
            return {
                'theme_settings': {
                    'primary_color': business.primary_color,
                    'secondary_color': business.secondary_color,
                    'primary_color_rgb': f"{primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}",
                    'secondary_color_rgb': f"{secondary_rgb[0]}, {secondary_rgb[1]}, {secondary_rgb[2]}",
                }
            }
        except Business.DoesNotExist:
            pass
    
    # Default values
    return {
        'theme_settings': {
            'primary_color': '#10b981',
            'secondary_color': '#6366f1',
            'primary_color_rgb': '16, 185, 129',
            'secondary_color_rgb': '99, 102, 241',
        }
    }