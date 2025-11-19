"""
Comando de Django para migrar imágenes de productos a Cloudinary
"""
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from apps.productos.models import Producto
import cloudinary.uploader
from cloudinary.models import CloudinaryResource


class Command(BaseCommand):
    help = 'Migra todas las imágenes de productos locales a Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la migración sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se harán cambios reales'))
        
        productos = Producto.objects.all()
        total = productos.count()
        migrados = 0
        errores = 0
        sin_imagen = 0
        
        self.stdout.write(f'\nEncontrados {total} productos\n')
        self.stdout.write('=' * 60)
        
        for i, producto in enumerate(productos, 1):
            self.stdout.write(f'\n[{i}/{total}] Procesando: {producto.nombre}')
            
            # Verificar si tiene imagen
            if not producto.imagen:
                self.stdout.write(self.style.WARNING('  ✗ Sin imagen'))
                sin_imagen += 1
                continue
            
            # Verificar si ya está en Cloudinary
            imagen_str = str(producto.imagen)
            if 'cloudinary' in imagen_str or 'res.cloudinary.com' in imagen_str:
                self.stdout.write(self.style.SUCCESS('  ✓ Ya está en Cloudinary'))
                migrados += 1
                continue
            
            # Intentar migrar
            try:
                # Verificar si el archivo existe localmente
                if hasattr(producto.imagen, 'path') and os.path.exists(producto.imagen.path):
                    if not dry_run:
                        # Subir a Cloudinary
                        result = cloudinary.uploader.upload(
                            producto.imagen.path,
                            folder='productos',
                            public_id=f'producto_{producto.id}_{producto.nombre[:30]}',
                            overwrite=True,
                            resource_type='image'
                        )
                        
                        # Actualizar el campo con la URL de Cloudinary
                        producto.imagen = result['secure_url']
                        producto.save()
                        
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrado: {result["secure_url"]}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Se migraría: {producto.imagen.path}'))
                    
                    migrados += 1
                else:
                    # El archivo no existe localmente, intentar descargar y subir
                    if not dry_run:
                        try:
                            # Intentar subir desde URL si es una URL
                            if producto.imagen.url:
                                result = cloudinary.uploader.upload(
                                    producto.imagen.url,
                                    folder='productos',
                                    public_id=f'producto_{producto.id}_{producto.nombre[:30]}',
                                    overwrite=True,
                                    resource_type='image'
                                )
                                
                                producto.imagen = result['secure_url']
                                producto.save()
                                
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Migrado desde URL: {result["secure_url"]}'))
                                migrados += 1
                            else:
                                raise Exception('No se puede acceder a la imagen')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                            errores += 1
                    else:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Archivo no encontrado: {producto.imagen}'))
                        errores += 1
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                errores += 1
        
        # Resumen
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('\n📊 RESUMEN DE MIGRACIÓN\n')
        self.stdout.write('=' * 60)
        self.stdout.write(f'\nTotal de productos: {total}')
        self.stdout.write(self.style.SUCCESS(f'✓ Migrados exitosamente: {migrados}'))
        self.stdout.write(self.style.WARNING(f'⚠ Sin imagen: {sin_imagen}'))
        self.stdout.write(self.style.ERROR(f'✗ Errores: {errores}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠ Esto fue una simulación. Ejecuta sin --dry-run para migrar realmente.'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ ¡Migración completada!'))
