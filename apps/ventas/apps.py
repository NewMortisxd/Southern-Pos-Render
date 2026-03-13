from django.apps import AppConfig


class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ventas'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import apps.ventas.signals
    
    def ready(self):
        """Importar señales cuando la app esté lista"""
        import apps.ventas.signals
