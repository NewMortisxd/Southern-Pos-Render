"""
Comando para crear vistas predefinidas útiles para los usuarios
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.productos.models_config import SavedProductFilter

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea vistas predefinidas útiles para los usuarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Email del usuario específico (opcional, si no se especifica se aplica a todos)',
        )

    def handle(self, *args, **options):
        user_email = options.get('user')
        
        if user_email:
            try:
                users = [User.objects.get(email=user_email)]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Usuario {user_email} no encontrado'))
                return
        else:
            users = User.objects.all()

        vistas_predefinidas = [
            {
                'nombre': 'Stock Bajo',
                'descripcion': 'Productos con stock por debajo del umbral',
                'filtros': {'stock_bajo': '1', 'orden': 'stock'},
                'icono': 'alert-triangle',
                'color': 'red',
            },
            {
                'nombre': 'Más Vendidos',
                'descripcion': 'Productos ordenados por popularidad',
                'filtros': {'orden': '-fecha_creacion'},
                'icono': 'trending-up',
                'color': 'emerald',
            },
            {
                'nombre': 'Sin Imagen',
                'descripcion': 'Productos que necesitan foto',
                'filtros': {'sin_imagen': '1'},
                'icono': 'image-off',
                'color': 'orange',
            },
            {
                'nombre': 'Vista Rápida',
                'descripcion': 'Lista compacta para operación rápida',
                'filtros': {'vista': 'list', 'orden': 'nombre'},
                'icono': 'zap',
                'color': 'blue',
            },
        ]

        created_count = 0
        skipped_count = 0

        for user in users:
            for vista_data in vistas_predefinidas:
                # Verificar si ya existe
                exists = SavedProductFilter.objects.filter(
                    user=user,
                    nombre=vista_data['nombre']
                ).exists()

                if not exists:
                    SavedProductFilter.objects.create(
                        user=user,
                        **vista_data
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Vista "{vista_data["nombre"]}" creada para {user.email}')
                    )
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {created_count} vistas creadas, {skipped_count} ya existían'
            )
        )
