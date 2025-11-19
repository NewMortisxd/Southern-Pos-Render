from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.productos.models import Categoria

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea una categoría "General" para todos los usuarios que no la tienen'

    def handle(self, *args, **options):
        usuarios = User.objects.all()
        creadas = 0
        
        for usuario in usuarios:
            # Verificar si el usuario ya tiene una categoría "General"
            if not Categoria.objects.filter(usuario_creador=usuario, nombre='General').exists():
                Categoria.objects.create(
                    nombre='General',
                    descripcion='Categoría general para productos sin clasificación específica',
                    usuario_creador=usuario
                )
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría "General" creada para {usuario.email}')
                )
        
        if creadas == 0:
            self.stdout.write(
                self.style.WARNING('Todos los usuarios ya tienen una categoría "General"')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Se crearon {creadas} categorías "General"')
            )
