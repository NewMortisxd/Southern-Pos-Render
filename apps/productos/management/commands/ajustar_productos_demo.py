from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.productos.models import Producto, Categoria
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Ajusta productos de la cuenta demo con precios y costos realistas'

    def handle(self, *args, **options):
        # Buscar el usuario
        try:
            user = User.objects.get(email='justinantonio2009@gmail.com')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Usuario no encontrado'))
            return

        # Obtener todos los productos del usuario
        productos = Producto.objects.filter(usuario_creador=user)
        
        if not productos.exists():
            self.stdout.write(self.style.WARNING('No hay productos para este usuario'))
            return

        # Buscar o crear categoría Bebidas
        categoria_bebidas, _ = Categoria.objects.get_or_create(
            nombre__icontains='bebida',
            usuario_creador=user,
            defaults={'nombre': 'Bebidas', 'descripcion': 'Bebidas y refrescos'}
        )

        count_updated = 0
        
        # Diccionario de precios sugeridos según tipo de producto
        precios_sugeridos = {
            # Bebidas
            'coca': {'precio': Decimal('1.50'), 'costo': Decimal('0.80')},
            'pepsi': {'precio': Decimal('1.50'), 'costo': Decimal('0.80')},
            'sprite': {'precio': Decimal('1.50'), 'costo': Decimal('0.80')},
            'fanta': {'precio': Decimal('1.50'), 'costo': Decimal('0.80')},
            'agua': {'precio': Decimal('0.75'), 'costo': Decimal('0.35')},
            'jugo': {'precio': Decimal('2.00'), 'costo': Decimal('1.00')},
            'cerveza': {'precio': Decimal('2.50'), 'costo': Decimal('1.50')},
            'vino': {'precio': Decimal('15.00'), 'costo': Decimal('8.00')},
            'café': {'precio': Decimal('1.50'), 'costo': Decimal('0.50')},
            'té': {'precio': Decimal('1.25'), 'costo': Decimal('0.40')},
            
            # Comidas
            'hamburguesa': {'precio': Decimal('8.50'), 'costo': Decimal('4.00')},
            'pizza': {'precio': Decimal('12.00'), 'costo': Decimal('5.50')},
            'pasta': {'precio': Decimal('9.00'), 'costo': Decimal('3.50')},
            'ensalada': {'precio': Decimal('6.50'), 'costo': Decimal('2.50')},
            'sopa': {'precio': Decimal('5.00'), 'costo': Decimal('2.00')},
            'sandwich': {'precio': Decimal('5.50'), 'costo': Decimal('2.50')},
            'hot dog': {'precio': Decimal('4.00'), 'costo': Decimal('1.80')},
            'taco': {'precio': Decimal('3.50'), 'costo': Decimal('1.50')},
            'burrito': {'precio': Decimal('7.00'), 'costo': Decimal('3.20')},
            'pollo': {'precio': Decimal('10.00'), 'costo': Decimal('5.00')},
            'carne': {'precio': Decimal('12.00'), 'costo': Decimal('6.50')},
            'pescado': {'precio': Decimal('14.00'), 'costo': Decimal('7.00')},
            'arroz': {'precio': Decimal('4.00'), 'costo': Decimal('1.50')},
            'papas': {'precio': Decimal('3.50'), 'costo': Decimal('1.20')},
            'frita': {'precio': Decimal('3.50'), 'costo': Decimal('1.20')},
            
            # Postres
            'helado': {'precio': Decimal('3.50'), 'costo': Decimal('1.50')},
            'pastel': {'precio': Decimal('4.50'), 'costo': Decimal('2.00')},
            'brownie': {'precio': Decimal('3.00'), 'costo': Decimal('1.20')},
            'flan': {'precio': Decimal('3.50'), 'costo': Decimal('1.50')},
            'cheesecake': {'precio': Decimal('5.00'), 'costo': Decimal('2.50')},
            'galleta': {'precio': Decimal('1.50'), 'costo': Decimal('0.60')},
            
            # Desayunos
            'huevo': {'precio': Decimal('5.00'), 'costo': Decimal('2.00')},
            'pancake': {'precio': Decimal('6.00'), 'costo': Decimal('2.50')},
            'waffle': {'precio': Decimal('6.50'), 'costo': Decimal('2.80')},
            'tostada': {'precio': Decimal('3.00'), 'costo': Decimal('1.00')},
            'cereal': {'precio': Decimal('4.00'), 'costo': Decimal('1.50')},
            'yogurt': {'precio': Decimal('3.50'), 'costo': Decimal('1.50')},
        }

        for producto in productos:
            nombre_lower = producto.nombre.lower()
            
            # Determinar si es bebida
            es_bebida = any(keyword in nombre_lower for keyword in [
                'coca', 'pepsi', 'sprite', 'fanta', 'agua', 'jugo', 'cerveza',
                'vino', 'café', 'té', 'refresco', 'gaseosa', 'soda', 'bebida'
            ])
            
            # Ajustar stock
            if es_bebida:
                producto.stock = 300
                producto.controla_stock = True
            else:
                # Servicios o productos sin stock
                producto.stock = 0
                producto.controla_stock = False
            
            # Buscar precio sugerido
            precio_encontrado = False
            for keyword, valores in precios_sugeridos.items():
                if keyword in nombre_lower:
                    # Calcular precio base (sin IVA) desde el precio con IVA
                    precio_con_iva = valores['precio']
                    producto.precio_base = precio_con_iva / Decimal('1.15')  # Asumiendo 15% IVA
                    producto.costo = valores['costo']
                    precio_encontrado = True
                    break
            
            # Si no se encontró precio específico, usar precio genérico según tipo
            if not precio_encontrado:
                if es_bebida:
                    precio_con_iva = Decimal('1.50')
                    producto.precio_base = precio_con_iva / Decimal('1.15')
                    producto.costo = Decimal('0.80')
                elif any(word in nombre_lower for word in ['plato', 'comida', 'almuerzo', 'cena']):
                    precio_con_iva = Decimal('10.00')
                    producto.precio_base = precio_con_iva / Decimal('1.15')
                    producto.costo = Decimal('4.50')
                elif any(word in nombre_lower for word in ['postre', 'dulce', 'torta']):
                    precio_con_iva = Decimal('4.00')
                    producto.precio_base = precio_con_iva / Decimal('1.15')
                    producto.costo = Decimal('1.80')
                else:
                    # Precio genérico
                    precio_con_iva = Decimal('7.50')
                    producto.precio_base = precio_con_iva / Decimal('1.15')
                    producto.costo = Decimal('3.50')
            
            # Asegurar que incluye IVA esté marcado
            producto.incluye_iva = True
            
            # Guardar cambios
            producto.save()
            count_updated += 1
            
            # Mostrar información
            self.stdout.write(
                f'✓ {producto.nombre}: '
                f'Precio=${float(producto.precio):.2f}, '
                f'Costo=${float(producto.costo):.2f}, '
                f'Stock={producto.stock if producto.controla_stock else "N/A"}'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Se actualizaron {count_updated} productos exitosamente.\n'
                f'   - Bebidas: Stock de 300 unidades\n'
                f'   - Otros productos: Sin control de stock\n'
                f'   - Todos con precios y costos realistas\n'
            )
        )
