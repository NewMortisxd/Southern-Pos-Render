from django.core.management.base import BaseCommand
from apps.productos.models import Producto
from decimal import Decimal

class Command(BaseCommand):
    help = 'Establece costos por defecto para productos existentes (70% del precio base)'

    def handle(self, *args, **options):
        productos_sin_costo = Producto.objects.filter(costo__isnull=True)
        count = 0
        
        for producto in productos_sin_costo:
            # Establecer costo como 70% del precio base (margen del 30%)
            # Esto es solo un valor por defecto, el usuario debe ajustarlo
            producto.costo = producto.precio_base * Decimal('0.70')
            producto.save()
            count += 1
            
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Se establecieron costos por defecto para {count} productos.\n'
                f'⚠️  IMPORTANTE: Estos son valores estimados (70% del precio base).\n'
                f'   Debes actualizar los costos reales en la gestión de productos.'
            )
        )
