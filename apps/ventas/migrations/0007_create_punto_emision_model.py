# Generated manually for punto emision model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        ('ventas', '0006_add_facturacion_electronica'),
    ]

    operations = [
        # Crear modelo PuntoEmision
        migrations.CreateModel(
            name='PuntoEmision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(
                    max_length=3,
                    verbose_name='Código Punto Emisión',
                    help_text='3 dígitos (ej: 001, 002)'
                )),
                ('nombre', models.CharField(
                    max_length=100,
                    verbose_name='Nombre',
                    help_text='Ej: Caja 1, Caja Principal, Sucursal Norte'
                )),
                ('establecimiento_codigo', models.CharField(
                    max_length=3,
                    verbose_name='Código Establecimiento',
                    help_text='3 dígitos (ej: 001)'
                )),
                ('secuencial_actual', models.PositiveIntegerField(
                    default=1,
                    verbose_name='Secuencial Actual',
                    help_text='Se autoincrementa con cada factura. NO modificar manualmente.'
                )),
                ('activo', models.BooleanField(
                    default=True,
                    verbose_name='Activo'
                )),
                ('business', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='puntos_emision',
                    to='usuarios.business',
                    verbose_name='Negocio'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
            ],
            options={
                'verbose_name': 'Punto de Emisión',
                'verbose_name_plural': 'Puntos de Emisión',
                'ordering': ['establecimiento_codigo', 'codigo'],
            },
        ),
        
        # Unique constraint: Un negocio no puede tener dos puntos con el mismo código en el mismo establecimiento
        migrations.AddConstraint(
            model_name='puntoemision',
            constraint=models.UniqueConstraint(
                fields=['business', 'establecimiento_codigo', 'codigo'],
                name='unique_punto_emision_por_negocio'
            ),
        ),
        
        # Agregar relación opcional de Venta a PuntoEmision
        migrations.AddField(
            model_name='venta',
            name='punto_emision',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ventas',
                to='ventas.puntoemision',
                verbose_name='Punto de Emisión'
            ),
        ),
        
        # Unique constraint multi-tenant para número de factura
        migrations.AddConstraint(
            model_name='venta',
            constraint=models.UniqueConstraint(
                fields=['usuario_creador', 'numero_factura'],
                name='unique_numero_factura_por_usuario',
                condition=models.Q(numero_factura__isnull=False)
            ),
        ),
    ]
