from django.core.management.base import BaseCommand
from apps.productos.models import Producto

class Command(BaseCommand):
    help = 'Migra metadata a productos existentes (tipo, unidad, stock mínimo, SKU)'

    def handle(self, *args, **options):
        productos = Producto.objects.all()
        count = 0
        
        for producto in productos:
            actualizado = False
            
            # Tipo de producto: detectar automáticamente
            if not producto.tipo_producto or producto.tipo_producto == 'fisico':
                nombre_lower = producto.nombre.lower()
                if any(word in nombre_lower for word in ['servicio', 'instalación', 'reparación', 'mantenimiento']):
                    producto.tipo_producto = 'servicio'
                    actualizado = True
                elif any(word in nombre_lower for word in ['combo', 'plato', 'menú', 'especial']):
                    producto.tipo_producto = 'combo'
                    actualizado = True
                elif any(word in nombre_lower for word in ['insumo', 'materia', 'ingrediente']):
                    producto.tipo_producto = 'insumo'
                    actualizado = True
                else:
                    producto.tipo_producto = 'fisico'
                    actualizado = True
            
            # Unidad de medida: detectar automáticamente
            if not producto.unidad_medida or producto.unidad_medida == 'unidad':
                nombre_lower = producto.nombre.lower()
                if any(word in nombre_lower for word in ['porción', 'plato', 'combo', 'menú']):
                    producto.unidad_medida = 'porcion'
                    actualizado = True
                elif any(word in nombre_lower for word in ['kg', 'kilo', 'kilogramo']):
                    producto.unidad_medida = 'kg'
                    actualizado = True
                elif any(word in nombre_lower for word in ['litro', 'lt']):
                    producto.unidad_medida = 'l'
                    actualizado = True
                elif any(word in nombre_lower for word in ['caja', 'cajas']):
                    producto.unidad_medida = 'caja'
                    actualizado = True
                else:
                    producto.unidad_medida = 'unidad'
                    actualizado = True
            
            # Stock mínimo: establecer por defecto si no existe
            if producto.stock_minimo is None:
                if producto.controla_stock:
                    # Stock mínimo basado en el stock actual
                    if producto.stock and producto.stock > 0:
                        producto.stock_minimo = max(5, int(producto.stock * 0.2))  # 20% del stock actual, mínimo 5
                    else:
                        producto.stock_minimo = 5
                    actualizado = True
            
            # SKU: generar automáticamente si no existe
            if not producto.sku:
                # Generar SKU basado en categoría y nombre
                if producto.categoria:
                    cat_prefix = producto.categoria.nombre[:3].upper()
                else:
                    cat_prefix = 'PRD'
                
                # Primeras 3 letras del nombre + ID
                nombre_prefix = ''.join(c for c in producto.nombre if c.isalnum())[:3].upper()
                producto.sku = f"{cat_prefix}-{nombre_prefix}-{producto.id}"
                actualizado = True
            
            if actualizado:
                producto.save()
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Se actualizaron {count} productos con metadata.\n'
                f'   - Tipo de producto asignado\n'
                f'   - Unidad de medida establecida\n'
                f'   - Stock mínimo configurado\n'
                f'   - SKU generado automáticamente'
            )
        )
