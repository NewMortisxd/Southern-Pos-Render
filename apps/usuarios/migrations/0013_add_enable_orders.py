# Generated migration for enable_orders field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0012_add_restaurant_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='enable_orders',
            field=models.BooleanField(
                default=False,
                verbose_name='Habilitar Sistema de Órdenes'
            ),
        ),
        migrations.AlterField(
            model_name='business',
            name='enable_kds',
            field=models.BooleanField(
                default=False,
                verbose_name='Mostrar Pantalla de Cocina en Sidebar'
            ),
        ),
        migrations.AlterField(
            model_name='business',
            name='enable_public_display',
            field=models.BooleanField(
                default=False,
                verbose_name='Mostrar Pantalla Pública en Sidebar'
            ),
        ),
    ]
