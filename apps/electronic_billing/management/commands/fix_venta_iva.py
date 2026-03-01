"""
Comando Django para corregir los valores de IVA en ventas existentes.
Uso: python manage.py fix_venta_iva
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.ventas.models import Venta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Corrige los valores de subtotal e IVA en ventas existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se haría sin aplicar cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Obtener ventas con IVA = 0 (incorrectas)
        ventas_incorrectas = Venta.objects.filter(iva=0).select_related('usuario_creador')
        total_ventas = ventas_incorrectas.count()
        
        if total_ventas == 0:
            self.stdout.write(self.style.SUCCESS('✅ No hay ventas que corregir'))
            return
        
        self.stdout.write(f'\n📊 Ventas a corregir: {total_ventas}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  Modo DRY RUN - No se aplicarán cambios\n'))
        else:
            self.stdout.write(self.style.WARNING('\n🔄 Aplicando correcciones...\n'))
        
        corregidas = 0
        errores = 0
        
        with transaction.atomic():
            for venta in ventas_incorrectas:
                try:
                    # Get IVA rate from business settings
                    try:
                        from apps.usuarios.models import Business
                        business = Business.objects.get(user=venta.usuario_creador)
                        tax_rate = business.iva_porcentaje / Decimal('100')
                    except:
                        tax_rate = Decimal('0.12')  # Default 12% for Ecuador
                    
                    # El total es correcto (lo que pagó el cliente)
                    total_con_iva = venta.total
                    
                    # Calcular base e IVA correctamente usando la tasa del negocio
                    base_sin_iva = total_con_iva / (Decimal('1') + tax_rate)
                    iva_calculado = total_con_iva - base_sin_iva
                    
                    # Redondear a 2 decimales
                    base_sin_iva = base_sin_iva.quantize(Decimal('0.01'))
                    iva_calculado = iva_calculado.quantize(Decimal('0.01'))
                    
                    # Verificar que la suma sea correcta
                    total_verificado = base_sin_iva + iva_calculado
                    diferencia = abs(total_con_iva - total_verificado)
                    
                    if diferencia > Decimal('0.01'):
                        self.stdout.write(
                            self.style.ERROR(
                                f'❌ Venta #{venta.id}: Diferencia de redondeo ${diferencia}'
                            )
                        )
                        errores += 1
                        continue
                    
                    # Mostrar cambio
                    self.stdout.write(
                        f'Venta #{venta.id}: '
                        f'${total_con_iva} → Base ${base_sin_iva} + IVA ${iva_calculado}'
                    )
                    
                    # Aplicar cambios si no es dry-run
                    if not dry_run:
                        venta.subtotal = base_sin_iva
                        venta.iva = iva_calculado
                        venta.save()
                    
                    corregidas += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error en venta #{venta.id}: {str(e)}')
                    )
                    errores += 1
            
            # Si es dry-run, hacer rollback
            if dry_run:
                transaction.set_rollback(True)
        
        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'Total ventas procesadas: {total_ventas}')
        self.stdout.write(self.style.SUCCESS(f'✅ Corregidas: {corregidas}'))
        
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errores: {errores}'))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Ejecuta sin --dry-run para aplicar los cambios'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Migración completada'))
