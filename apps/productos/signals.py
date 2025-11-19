from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Categoria

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_categoria_general(sender, instance, created, **kwargs):
    """
    Crea automáticamente una categoría 'General' cuando se crea un nuevo usuario
    """
    if created:
        Categoria.objects.create(
            nombre='General',
            descripcion='Categoría general para productos sin clasificación específica',
            usuario_creador=instance
        )
