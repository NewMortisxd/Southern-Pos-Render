from django.core.management.base import BaseCommand
from apps.ventas.models import DetalleVenta

class Command(BaseCommand):
    help = 'Migra los nombres de productos a los detalles de venta existentes'

    def handle(self, *args, **options):
        detalles = DetalleVenta.objects.filter(nombre_producto='Producto')
        count = 0
        
        for detalle in detalles:
            if detalle.producto:
                detalle.nombre_producto = detalle.producto.nombre
                detalle.codigo_producto = detalle.producto.codigo_barras
                detalle.save()
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Se migraron {count} detalles de venta con nombres de productos.'
            )
        )
