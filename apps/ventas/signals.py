"""
Signals para el módulo de ventas
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.usuarios.models import Business
from apps.ventas.models import PuntoEmision


@receiver(post_save, sender=Business)
def crear_punto_emision_por_defecto(sender, instance, created, **kwargs):
    """
    Crea un punto de emisión por defecto (001-001) cuando se crea un Business.
    
    Esto garantiza que cada negocio tenga al menos un punto de emisión
    para poder generar facturas desde el inicio.
    """
    if created:
        # Crear punto de emisión por defecto
        PuntoEmision.objects.get_or_create(
            business=instance,
            codigo='001',
            establecimiento_codigo='001',
            defaults={
                'nombre': 'Caja Principal',
                'secuencial_actual': 1,
                'activo': True
            }
        )
