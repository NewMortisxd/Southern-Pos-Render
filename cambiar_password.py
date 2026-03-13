"""
Script para cambiar la contraseña de un usuario
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'southern_food_pos.settings')
django.setup()

from apps.usuarios.models import Usuario

def cambiar_password():
    """
    Cambia la contraseña del usuario jany_molina@hotmail.com a 1234
    """
    email = 'jany_molina@hotmail.com'
    nueva_password = '1234'
    
    print("=" * 80)
    print("🔐 CAMBIO DE CONTRASEÑA")
    print("=" * 80)
    
    try:
        usuario = Usuario.objects.get(email=email)
        
        print(f"\n✅ Usuario encontrado:")
        print(f"   - Email: {usuario.email}")
        print(f"   - Nombre: {usuario.get_full_name()}")
        print(f"   - Username: {usuario.username}")
        
        # Cambiar la contraseña
        usuario.set_password(nueva_password)
        usuario.save()
        
        print(f"\n✅ Contraseña cambiada exitosamente a: {nueva_password}")
        print(f"\n📝 Credenciales de acceso:")
        print(f"   - Email/Username: {email}")
        print(f"   - Contraseña: {nueva_password}")
        
    except Usuario.DoesNotExist:
        print(f"\n❌ No se encontró el usuario con email: {email}")
    except Exception as e:
        print(f"\n❌ Error al cambiar la contraseña: {e}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    cambiar_password()
