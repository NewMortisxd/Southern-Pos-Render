"""
Comando para migrar precios desde el campo antiguo 'precio' al nuevo 'precio_base'.

Este comando usa SQL directo para acceder al campo 'precio' que ya fue eliminado
del modelo pero aún existe en la base de datos.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from decimal import Decimal


class Command(BaseCommand):
    help = 'Migra precios desde el campo antiguo precio al nuevo precio_base'

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
        
        with connection.cursor() as cursor:
            # Verificar si el campo 'precio' aún existe en la tabla
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='productos_producto' AND column_name='precio'
            """)
            
            if not cursor.fetchone():
                self.stdout.write(
                    self.style.ERROR(
                        'El campo "precio" ya no existe en la base de datos. '
                        'La migración ya fue completada o el campo nunca existió.'
                    )
                )
                return
            
            # Obtener productos con precio_base=0 pero que tienen precio antiguo
            cursor.execute("""
                SELECT id, nombre, precio, precio_base
                FROM productos_producto
                WHERE precio_base = 0 AND precio > 0
            """)
            
            productos = cursor.fetchall()
            
            if not productos:
                self.stdout.write(
                    self.style.SUCCESS(
                        '✓ No hay productos que migrar. Todos los precios están actualizados.'
                    )
                )
                return
            
            self.stdout.write(f'\nEncontrados {len(productos)} productos para migrar:')
            self.stdout.write('='*70)
            
            for producto in productos:
                id_producto, nombre, precio_antiguo, precio_base_actual = producto
                
                # Calcular precio_base (precio antiguo ya tenía IVA del 15%)
                precio_con_iva = Decimal(str(precio_antiguo))
                precio_base_nuevo = precio_con_iva / Decimal('1.15')
                
                self.stdout.write(
                    f'\nID: {id_producto} | {nombre}'
                )
                self.stdout.write(f'  Precio antiguo (con IVA): ${precio_con_iva}')
                self.stdout.write(f'  Precio base nuevo (sin IVA): ${precio_base_nuevo:.2f}')
                self.stdout.write(f'  Precio final calculado: ${precio_con_iva}')
            
            if not dry_run:
                confirmar = input(
                    f'\n¿Deseas migrar estos {len(productos)} productos? (si/no): '
                )
                
                if confirmar.lower() not in ['si', 's', 'yes', 'y']:
                    self.stdout.write(self.style.WARNING('\nMigración cancelada'))
                    return
                
                with transaction.atomic():
                    # Actualizar precio_base calculando desde precio antiguo
                    cursor.execute("""
                        UPDATE productos_producto
                        SET precio_base = precio / 1.15,
                            incluye_iva = TRUE
                        WHERE precio_base = 0 AND precio > 0
                    """)
                    
                    actualizados = cursor.rowcount
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✓ {actualizados} productos migrados exitosamente'
                        )
                    )
                    
                    # Mostrar resumen
                    cursor.execute("""
                        SELECT id, nombre, precio_base, precio
                        FROM productos_producto
                        WHERE id IN (
                            SELECT id FROM productos_producto 
                            WHERE precio > 0 
                            LIMIT 5
                        )
                    """)
                    
                    self.stdout.write('\n' + '='*70)
                    self.stdout.write('Muestra de productos migrados:')
                    for prod in cursor.fetchall():
                        id_p, nombre_p, precio_base_p, precio_p = prod
                        precio_final = Decimal(str(precio_base_p)) * Decimal('1.15')
                        self.stdout.write(
                            f'  {nombre_p}: base=${precio_base_p:.2f}, '
                            f'final=${precio_final:.2f}'
                        )
            else:
                self.stdout.write('\n' + self.style.WARNING('DRY RUN - No se guardaron cambios'))
