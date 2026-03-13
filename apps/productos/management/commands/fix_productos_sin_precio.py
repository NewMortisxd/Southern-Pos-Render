"""
Comando para identificar y opcionalmente fijar productos sin precio base.

Este comando ayuda a identificar productos que tienen precio_base=0
y necesitan ser configurados.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.productos.models import Producto
from apps.usuarios.models import Business


class Command(BaseCommand):
    help = 'Identifica productos con precio_base=0 y permite configurarlos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Intenta fijar productos asignando un precio base de ejemplo',
        )
        parser.add_argument(
            '--precio-default',
            type=float,
            default=10.0,
            help='Precio base por defecto para productos sin precio (default: 10.0)',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        precio_default = Decimal(str(options['precio_default']))
        
        # Buscar productos con precio_base = 0
        productos_sin_precio = Producto.objects.filter(precio_base=0)
        total = productos_sin_precio.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ Todos los productos tienen precio configurado'))
            return
        
        self.stdout.write(f'\nEncontrados {total} productos sin precio base:')
        self.stdout.write('='*70)
        
        for producto in productos_sin_precio:
            # Obtener IVA del negocio
            iva_porcentaje = Decimal('15')
            try:
                business = Business.objects.filter(user=producto.usuario_creador).first()
                if business and business.iva_porcentaje:
                    iva_porcentaje = business.iva_porcentaje
            except:
                pass
            
            precio_con_iva = precio_default * (Decimal('1') + iva_porcentaje / Decimal('100'))
            
            self.stdout.write(
                f'\nID: {producto.id} | {producto.nombre} | '
                f'Usuario: {producto.usuario_creador.username if producto.usuario_creador else "N/A"}'
            )
            self.stdout.write(f'  Precio base actual: ${producto.precio_base}')
            self.stdout.write(f'  IVA del negocio: {iva_porcentaje}%')
            
            if fix_mode:
                self.stdout.write(
                    f'  → Asignando precio_base: ${precio_default} '
                    f'(precio final con IVA: ${precio_con_iva})'
                )
        
        if fix_mode:
            confirmar = input(
                f'\n¿Deseas asignar precio_base=${precio_default} a estos {total} productos? (si/no): '
            )
            
            if confirmar.lower() in ['si', 's', 'yes', 'y']:
                with transaction.atomic():
                    actualizados = productos_sin_precio.update(
                        precio_base=precio_default,
                        incluye_iva=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✓ {actualizados} productos actualizados con precio_base=${precio_default}'
                        )
                    )
            else:
                self.stdout.write(self.style.WARNING('\nOperación cancelada'))
        else:
            self.stdout.write('\n' + '='*70)
            self.stdout.write(
                self.style.WARNING(
                    f'\nPara fijar estos productos con un precio por defecto, ejecuta:'
                )
            )
            self.stdout.write(
                self.style.SQL_KEYWORD(
                    f'python manage.py fix_productos_sin_precio --fix --precio-default=10.0'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '\nO actualízalos manualmente desde el panel de administración.'
                )
            )
