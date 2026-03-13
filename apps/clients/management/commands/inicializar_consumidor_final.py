from django.core.management.base import BaseCommand
from apps.clients.models import Cliente
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Inicializa el cliente "Consumidor Final" para el sistema POS'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Inicializando cliente Consumidor Final...'))
        
        # Obtener el primer usuario del sistema (admin)
        try:
            usuario_sistema = Usuario.objects.first()
            if not usuario_sistema:
                self.stdout.write(self.style.ERROR('❌ No hay usuarios en el sistema. Crea un usuario primero.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al obtener usuario: {e}'))
            return

        # Verificar si ya existe Consumidor Final
        consumidor_final = Cliente.objects.filter(identificacion='9999999999').first()
        
        if consumidor_final:
            # Actualizar datos si ya existe
            consumidor_final.nombre = 'Consumidor Final'
            consumidor_final.razon_social = 'CONSUMIDOR FINAL'
            consumidor_final.telefono = None
            consumidor_final.email = None
            consumidor_final.direccion = 'N/A'
            consumidor_final.ciudad = 'N/A'
            consumidor_final.grupo = 'regular'
            consumidor_final.estado = 'activo'
            consumidor_final.credito = 0
            consumidor_final.cupo = 0
            consumidor_final.tasa_descuento = 0
            consumidor_final.tasa_recargo = 0
            consumidor_final.es_favorito = False
            consumidor_final.usuario_creador = usuario_sistema
            consumidor_final.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cliente "Consumidor Final" actualizado (ID: {consumidor_final.id})')
            )
        else:
            # Crear nuevo Consumidor Final
            try:
                consumidor_final = Cliente.objects.create(
                    codigo='CF-001',
                    nombre='Consumidor Final',
                    razon_social='CONSUMIDOR FINAL',
                    identificacion='9999999999',
                    telefono=None,
                    email=None,
                    direccion='N/A',
                    ciudad='N/A',
                    grupo='regular',
                    estado='activo',
                    credito=0,
                    cupo=0,
                    tasa_descuento=0,
                    tasa_recargo=0,
                    comentarios='Cliente por defecto para ventas sin identificación. NO ELIMINAR.',
                    es_favorito=False,
                    usuario_creador=usuario_sistema
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cliente "Consumidor Final" creado exitosamente (ID: {consumidor_final.id})')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error al crear Consumidor Final: {e}')
                )
                return

        # Mostrar información
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════'))
        self.stdout.write(self.style.SUCCESS('  CONSUMIDOR FINAL INICIALIZADO'))
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════'))
        self.stdout.write(f'  ID: {consumidor_final.id}')
        self.stdout.write(f'  Nombre: {consumidor_final.nombre}')
        self.stdout.write(f'  Identificación: {consumidor_final.identificacion}')
        self.stdout.write(f'  Estado: {consumidor_final.estado}')
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📝 IMPORTANTE:'))
        self.stdout.write('   - Este cliente se usa para ventas sin identificación')
        self.stdout.write('   - NO puede comprar a crédito')
        self.stdout.write('   - NO debe ser eliminado del sistema')
        self.stdout.write('   - Se usa automáticamente en el POS')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Inicialización completada'))
