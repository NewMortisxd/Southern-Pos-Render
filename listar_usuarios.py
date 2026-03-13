"""
Script para listar todos los usuarios de la base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'southern_food_pos.settings')
django.setup()

from apps.usuarios.models import Usuario

def listar_usuarios():
    """
    Lista todos los usuarios de la base de datos
    """
    print("=" * 80)
    print("📋 LISTADO DE USUARIOS EN LA BASE DE DATOS")
    print("=" * 80)
    
    usuarios = Usuario.objects.all()
    
    if not usuarios:
        print("\n❌ No hay usuarios en la base de datos")
        return
    
    print(f"\n✅ Total de usuarios: {usuarios.count()}\n")
    
    for i, usuario in enumerate(usuarios, 1):
        print(f"{i}. Usuario: {usuario.username}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Nombre: {usuario.get_full_name() or 'N/A'}")
        print(f"   - Superusuario: {'Sí' if usuario.is_superuser else 'No'}")
        print(f"   - Staff: {'Sí' if usuario.is_staff else 'No'}")
        print(f"   - Activo: {'Sí' if usuario.is_active else 'No'}")
        print(f"   - Fecha registro: {usuario.date_joined.strftime('%d/%m/%Y %H:%M')}")
        
        # Mostrar información del negocio si existe
        try:
            if hasattr(usuario, 'business'):
                business = usuario.business
                print(f"   - Negocio: {business.nombre_negocio}")
                print(f"   - RUC: {business.ruc_negocio}")
        except:
            pass
        
        print()
    
    print("=" * 80)

if __name__ == '__main__':
    listar_usuarios()
