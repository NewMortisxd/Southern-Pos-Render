# Generated migration for ProductDisplayConfig

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('productos', '0007_alter_producto_imagen'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedProductFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Filtro')),
                ('filtros', models.JSONField(default=dict, verbose_name='Filtros')),
                ('es_favorito', models.BooleanField(default=False, verbose_name='Filtro Favorito')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_product_filters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Filtro Guardado',
                'verbose_name_plural': 'Filtros Guardados',
                'ordering': ['-es_favorito', '-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='ProductDisplayConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vista_predeterminada', models.CharField(choices=[('grid', 'Vista Grid (Tarjetas)'), ('list', 'Vista Lista (Compacta)'), ('table', 'Vista Tabla (Detallada)')], default='grid', max_length=10, verbose_name='Vista Predeterminada')),
                ('orden_predeterminado', models.CharField(choices=[('nombre', 'Nombre A-Z'), ('-nombre', 'Nombre Z-A'), ('precio', 'Precio: Menor a Mayor'), ('-precio', 'Precio: Mayor a Menor'), ('stock', 'Stock: Menor a Mayor'), ('-stock', 'Stock: Mayor a Menor'), ('-fecha_creacion', 'Más Recientes'), ('fecha_creacion', 'Más Antiguos')], default='-fecha_creacion', max_length=20, verbose_name='Orden Predeterminado')),
                ('mostrar_imagenes', models.BooleanField(default=True, verbose_name='Mostrar Imágenes')),
                ('mostrar_codigo_barras', models.BooleanField(default=True, verbose_name='Mostrar Código de Barras')),
                ('mostrar_stock', models.BooleanField(default=True, verbose_name='Mostrar Stock')),
                ('mostrar_categoria', models.BooleanField(default=True, verbose_name='Mostrar Categoría')),
                ('mostrar_descripcion', models.BooleanField(default=False, verbose_name='Mostrar Descripción')),
                ('tamano_imagen_grid', models.CharField(choices=[('small', 'Pequeño'), ('medium', 'Mediano'), ('large', 'Grande')], default='medium', max_length=10, verbose_name='Tamaño de Imagen en Grid')),
                ('filtros_avanzados_activos', models.BooleanField(default=True, verbose_name='Activar Filtros Avanzados')),
                ('busqueda_codigo_barras_prioritaria', models.BooleanField(default=False, verbose_name='Priorizar Búsqueda por Código de Barras')),
                ('alerta_stock_bajo', models.BooleanField(default=True, verbose_name='Mostrar Alerta de Stock Bajo')),
                ('umbral_stock_bajo', models.PositiveIntegerField(default=10, verbose_name='Umbral de Stock Bajo')),
                ('productos_por_pagina', models.PositiveIntegerField(default=20, verbose_name='Productos por Página')),
                ('auto_configurar_por_modo', models.BooleanField(default=True, verbose_name='Auto-configurar según Modo de Operación')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='product_display_config', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Configuración de Vista de Productos',
                'verbose_name_plural': 'Configuraciones de Vista de Productos',
            },
        ),
    ]
