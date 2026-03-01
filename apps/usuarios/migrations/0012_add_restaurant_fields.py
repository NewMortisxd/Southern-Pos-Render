# Generated migration for Business restaurant fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0011_business_modo_operacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='business_type',
            field=models.CharField(
                choices=[
                    ('restaurant', 'Restaurante'),
                    ('retail', 'Retail/Supermercado'),
                    ('hybrid', 'Híbrido')
                ],
                default='restaurant',
                max_length=20,
                verbose_name='Tipo de Negocio'
            ),
        ),
        migrations.AddField(
            model_name='business',
            name='enable_kds',
            field=models.BooleanField(
                default=False,
                verbose_name='Habilitar KDS (Kitchen Display System)'
            ),
        ),
        migrations.AddField(
            model_name='business',
            name='enable_public_display',
            field=models.BooleanField(
                default=False,
                verbose_name='Habilitar Pantalla Pública'
            ),
        ),
        migrations.AddField(
            model_name='business',
            name='last_order_number',
            field=models.PositiveIntegerField(
                default=0,
                verbose_name='Último Número de Orden'
            ),
        ),
    ]
