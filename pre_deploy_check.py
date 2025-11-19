#!/usr/bin/env python
"""
Script para verificar que todo esté listo para el despliegue en Render
"""
import os
import sys

def check_file_exists(filepath, description):
    """Verifica si un archivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NO ENCONTRADO: {filepath}")
        return False

def check_file_content(filepath, search_string, description):
    """Verifica si un archivo contiene cierto contenido"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - No encontrado en {filepath}")
                return False
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {filepath}")
        return False
    except Exception as e:
        print(f"⚠️  Error al leer {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 VERIFICACIÓN PRE-DESPLIEGUE PARA RENDER")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Verificar archivos esenciales
    print("📁 Verificando archivos esenciales...")
    print("-" * 60)
    all_checks_passed &= check_file_exists('build.sh', 'Script de construcción')
    all_checks_passed &= check_file_exists('render.yaml', 'Configuración de Render')
    all_checks_passed &= check_file_exists('requirements.txt', 'Dependencias de Python')
    all_checks_passed &= check_file_exists('runtime.txt', 'Versión de Python')
    all_checks_passed &= check_file_exists('gunicorn_config.py', 'Configuración de Gunicorn')
    all_checks_passed &= check_file_exists('.gitignore', 'Archivo .gitignore')
    all_checks_passed &= check_file_exists('manage.py', 'Django manage.py')
    print()
    
    # Verificar configuración de Django
    print("⚙️  Verificando configuración de Django...")
    print("-" * 60)
    settings_path = 'southern_food_pos/settings.py'
    all_checks_passed &= check_file_content(
        settings_path, 
        'whitenoise', 
        'WhiteNoise configurado'
    )
    all_checks_passed &= check_file_content(
        settings_path, 
        'dj_database_url', 
        'dj-database-url importado'
    )
    all_checks_passed &= check_file_content(
        settings_path, 
        'from decouple import config', 
        'python-decouple configurado'
    )
    all_checks_passed &= check_file_content(
        settings_path, 
        'RENDER_EXTERNAL_HOSTNAME', 
        'RENDER_EXTERNAL_HOSTNAME configurado'
    )
    all_checks_passed &= check_file_content(
        settings_path, 
        'STATIC_ROOT', 
        'STATIC_ROOT configurado'
    )
    print()
    
    # Verificar requirements.txt
    print("📦 Verificando dependencias...")
    print("-" * 60)
    all_checks_passed &= check_file_content(
        'requirements.txt', 
        'gunicorn', 
        'Gunicorn en requirements.txt'
    )
    all_checks_passed &= check_file_content(
        'requirements.txt', 
        'whitenoise', 
        'WhiteNoise en requirements.txt'
    )
    all_checks_passed &= check_file_content(
        'requirements.txt', 
        'psycopg2-binary', 
        'psycopg2-binary en requirements.txt'
    )
    all_checks_passed &= check_file_content(
        'requirements.txt', 
        'dj-database-url', 
        'dj-database-url en requirements.txt'
    )
    all_checks_passed &= check_file_content(
        'requirements.txt', 
        'python-decouple', 
        'python-decouple en requirements.txt'
    )
    print()
    
    # Verificar render.yaml
    print("🔧 Verificando render.yaml...")
    print("-" * 60)
    all_checks_passed &= check_file_content(
        'render.yaml', 
        'buildCommand', 
        'buildCommand configurado'
    )
    all_checks_passed &= check_file_content(
        'render.yaml', 
        'startCommand', 
        'startCommand configurado'
    )
    all_checks_passed &= check_file_content(
        'render.yaml', 
        'databases:', 
        'Base de datos configurada'
    )
    print()
    
    # Verificar build.sh
    print("🔨 Verificando build.sh...")
    print("-" * 60)
    all_checks_passed &= check_file_content(
        'build.sh', 
        'pip install -r requirements.txt', 
        'Instalación de dependencias'
    )
    all_checks_passed &= check_file_content(
        'build.sh', 
        'collectstatic', 
        'Recolección de archivos estáticos'
    )
    all_checks_passed &= check_file_content(
        'build.sh', 
        'migrate', 
        'Ejecución de migraciones'
    )
    print()
    
    # Verificar estructura de directorios
    print("📂 Verificando estructura de directorios...")
    print("-" * 60)
    all_checks_passed &= check_file_exists('apps', 'Directorio apps')
    all_checks_passed &= check_file_exists('static', 'Directorio static')
    all_checks_passed &= check_file_exists('templates', 'Directorio templates')
    print()
    
    # Resumen final
    print("=" * 60)
    if all_checks_passed:
        print("✅ ¡TODAS LAS VERIFICACIONES PASARON!")
        print()
        print("🚀 Tu aplicación está lista para desplegarse en Render.")
        print()
        print("Próximos pasos:")
        print("1. git add .")
        print("2. git commit -m 'Configuración para Render'")
        print("3. git push origin main")
        print("4. Ir a render.com y conectar tu repositorio")
        print()
        return 0
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print()
        print("Por favor, revisa los errores arriba y corrígelos antes de desplegar.")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
