"""
Script para migrar imágenes locales a Cloudinary
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'southern_food_pos.settings')
django.setup()

import cloudinary.uploader
from apps.productos.models import Producto

def migrate_images():
    """Migra todas las imágenes de productos a Cloudinary"""
    productos = Producto.objects.all()
    
    print(f"Encontrados {productos.count()} productos")
    
    for producto in productos:
        if producto.imagen and hasattr(producto.imagen, 'path'):
            try:
                # Verificar si el archivo existe localmente
                if os.path.exists(producto.imagen.path):
                    print(f"Subiendo imagen de: {producto.nombre}")
                    
                    # Subir a Cloudinary
                    result = cloudinary.uploader.upload(
                        producto.imagen.path,
                        folder="productos",
                        public_id=f"producto_{producto.id}",
                        overwrite=True
                    )
                    
                    # Actualizar la URL en el modelo
                    producto.imagen = result['secure_url']
                    producto.save()
                    
                    print(f"✓ Imagen subida: {result['secure_url']}")
                else:
                    print(f"✗ Archivo no encontrado: {producto.imagen.path}")
            except Exception as e:
                print(f"✗ Error subiendo {producto.nombre}: {e}")
        else:
            print(f"- {producto.nombre} no tiene imagen")
    
    print("\n¡Migración completada!")

if __name__ == '__main__':
    migrate_images()
