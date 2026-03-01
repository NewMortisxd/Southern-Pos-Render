# Generated migration for Order model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.PositiveIntegerField()),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendiente'),
                        ('PREPARING', 'En Preparación'),
                        ('READY', 'Listo'),
                        ('DELIVERED', 'Entregado'),
                        ('CANCELLED', 'Cancelado')
                    ],
                    default='PENDING',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('preparing_at', models.DateTimeField(blank=True, null=True)),
                ('ready_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('business', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='orders',
                    to='usuarios.business'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='venta',
            name='order',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='sale',
                to='ventas.order'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='order',
            unique_together={('business', 'order_number')},
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['business', 'status'], name='ventas_orde_busines_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['business', 'created_at'], name='ventas_orde_busines_created_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'created_at'], name='ventas_orde_status_created_idx'),
        ),
    ]
