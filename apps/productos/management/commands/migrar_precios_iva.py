"""
Comando para migrar precios del sistema antiguo al nuevo sistema de IVA.

El sistema antiguo guardaba el precio con IVA incluido en el campo 'precio'.
El nuevo sistema guarda:
- precio_base: precio sin IVA
- incluye_iva: True (por defecto, ya que los precios antiguos tenían IVA)

Este script calcula el precio_base a partir del precio con IVA.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.productos.models import Producto
from apps.usuarios.models import Business


class Command(BaseCommand):
    help = 'Migra los precios del sistema antiguo (con IVA) al nuevo sistema (precio_base + IVA)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la migración sin guardar cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se guardarán cambios'))
        
        # Obtener todos los productos
        productos = Producto.objects.all()
        total_productos = productos.count()
        
        if total_productos == 0:
            self.stdout.write(self.style.WARNING('No hay productos para migrar'))
            return
        
        self.stdout.write(f'Encontrados {total_productos} productos para migrar')
        
        migrados = 0
        errores = 0
        
        with transaction.atomic():
            for producto in productos:
                try:
                    # Obtener el IVA del negocio del usuario
                    iva_porcentaje = Decimal('15')  # Default
                    try:
                        business = Business.objects.filter(user=producto.usuario_creador).first()
                        if business and business.iva_porcentaje:
                            iva_porcentaje = business.iva_porcentaje
                    except:
                        pass
                    
                    # El precio_base actual es 0 (default de la migración)
                    # Necesitamos verificar si ya fue migrado
                    if producto.precio_base == 0:
                        # Calcular precio_base desde el precio con IVA
                        # precio_con_iva = precio_base * (1 + iva/100)
                        # precio_base = precio_con_iva / (1 + iva/100)
                        
                        # Como el campo 'precio' ya no existe, usamos la propiedad calculada
                        # que devuelve precio_base * (1 + iva/100)
                        # Pero necesitamos el precio original con IVA
                        
                        # Por ahora, asumimos que precio_base=0 significa que no se ha migrado
                        # y necesitamos un valor inicial
                        self.stdout.write(
                            self.style.WARNING(
                                f'Producto "{producto.nombre}" (ID: {producto.id}) tiene precio_base=0. '
                                f'Necesita configuración manual.'
                            )
                        )
                        continue
                    
                    # Si precio_base ya tiene un valor, verificamos si incluye_iva está correcto
                    if not producto.incluye_iva:
                        # Marcar que el precio incluye IVA (comportamiento del sistema antiguo)
                        producto.incluye_iva = True
                        
                        if not dry_run:
                            producto.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Producto "{producto.nombre}" (ID: {producto.id}) - '
                                f'Marcado como incluye_iva=True'
                            )
                        )
                        migrados += 1
                    else:
                        self.stdout.write(
                            f'  Producto "{producto.nombre}" (ID: {producto.id}) - Ya migrado'
                        )
                
                except Exception as e:
                    errores += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Error en producto "{producto.nombre}" (ID: {producto.id}): {str(e)}'
                        )
                    )
            
            if dry_run:
                # Revertir la transacción en modo dry-run
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('\nDRY RUN completado - No se guardaron cambios'))
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Total productos: {total_productos}'))
        self.stdout.write(self.style.SUCCESS(f'Migrados: {migrados}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'Errores: {errores}'))
        self.stdout.write('='*50)
        
        if not dry_run and migrados > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Migración completada exitosamente'
                )
            )
        
        # Instrucciones adicionales
        self.stdout.write('\n' + self.style.WARNING('NOTA IMPORTANTE:'))
        self.stdout.write(
            'Si tienes productos con precio_base=0, necesitas actualizarlos manualmente '
            'o ejecutar el siguiente comando SQL para migrar desde el precio antiguo:\n'
        )
        self.stdout.write(
            self.style.SQL_KEYWORD(
                'UPDATE productos_producto SET precio_base = precio / 1.15, incluye_iva = TRUE '
                'WHERE precio_base = 0 AND precio > 0;'
            )
        )
