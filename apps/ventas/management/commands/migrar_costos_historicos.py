from django.core.management.base import BaseCommand
from apps.ventas.models import DetalleVenta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Migra los costos de productos a los detalles de venta existentes'

    def handle(self, *args, **options):
        detalles = DetalleVenta.objects.filter(costo_unitario__isnull=True)
        count = 0
        
        for detalle in detalles:
            if detalle.producto and detalle.producto.costo:
                detalle.costo_unitario = detalle.producto.costo
                detalle.save()
                count += 1
            else:
                # Si no hay producto o no tiene costo, establecer en 0
                detalle.costo_unitario = Decimal('0')
                detalle.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Se migraron costos para {count} detalles de venta.\n'
                f'   Ahora los reportes históricos de utilidad serán precisos.'
            )
        )
