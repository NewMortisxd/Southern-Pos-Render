# Generated manually for electronic billing implementation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0005_add_costo_unitario_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='establecimiento_codigo',
            field=models.CharField(
                default='001',
                max_length=3,
                verbose_name='Código Establecimiento',
                help_text='3 dígitos del establecimiento (ej: 001)'
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='punto_emision_codigo',
            field=models.CharField(
                default='001',
                max_length=3,
                verbose_name='Código Punto Emisión',
                help_text='3 dígitos del punto de emisión (ej: 001)'
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='secuencial',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                verbose_name='Número Secuencial',
                help_text='Secuencial único de esta factura'
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='numero_factura',
            field=models.CharField(
                max_length=17,
                null=True,
                blank=True,
                unique=True,
                verbose_name='Número de Factura',
                help_text='Formato: 001-001-000000001'
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='clave_acceso',
            field=models.CharField(
                max_length=49,
                blank=True,
                null=True,
                verbose_name='Clave de Acceso SRI',
                help_text='Clave de 49 dígitos generada según SRI'
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='fecha_autorizacion',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Fecha de Autorización SRI'
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='estado_sri',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('PENDIENTE', 'Pendiente'),
                    ('AUTORIZADA', 'Autorizada'),
                    ('RECHAZADA', 'Rechazada'),
                    ('NO_AUTORIZADA', 'No Autorizada'),
                ],
                default='PENDIENTE',
                verbose_name='Estado SRI'
            ),
        ),
    ]
