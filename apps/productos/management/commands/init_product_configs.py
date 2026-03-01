"""
Comando para inicializar configuraciones de productos para usuarios existentes
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.productos.models_config import ProductDisplayConfig
from apps.usuarios.models import Business

User = get_user_model()


class Command(BaseCommand):
    help = 'Inicializa configuraciones de productos para usuarios existentes'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        updated_count = 0

        for user in users:
            config, created = ProductDisplayConfig.objects.get_or_create(user=user)
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Configuración creada para {user.username}')
                )
                
                # Intentar aplicar preset según modo de operación
                try:
                    business = Business.objects.get(user=user)
                    if business.modo_operacion == 'restaurante':
                        config.aplicar_preset_restaurante()
                        self.stdout.write(
                            self.style.SUCCESS(f'  → Preset Restaurante aplicado')
                        )
                    elif business.modo_operacion == 'retail':
                        config.aplicar_preset_retail()
                        self.stdout.write(
                            self.style.SUCCESS(f'  → Preset Retail aplicado')
                        )
                except Business.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ No se encontró negocio para {user.username}')
                    )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'○ Configuración ya existe para {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {created_count} creadas, {updated_count} existentes'
            )
        )
