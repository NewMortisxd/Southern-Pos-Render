# ✅ Checklist de Despliegue en Render

## Archivos creados:
- ✅ `build.sh` - Script de construcción
- ✅ `render.yaml` - Configuración automática de Render
- ✅ `runtime.txt` - Versión de Python
- ✅ `.gitignore` - Archivos a ignorar
- ✅ `.env.example` - Ejemplo de variables de entorno
- ✅ `requirements.txt` - Actualizado con todas las dependencias

## Cambios en settings.py:
- ✅ Configuración de variables de entorno con `python-decouple`
- ✅ Soporte para `DATABASE_URL` de Render
- ✅ WhiteNoise para archivos estáticos
- ✅ Configuración de seguridad para producción
- ✅ ALLOWED_HOSTS dinámico

## Pasos rápidos para desplegar:

### 1. Commit y push
```bash
git add .
git commit -m "Configuración para Render"
git push origin main
```

### 2. En Render.com
1. Crear cuenta en https://render.com
2. Conectar repositorio
3. Seleccionar "New +" → "Blueprint"
4. Render detectará `render.yaml` automáticamente
5. Click en "Apply"

### 3. Configurar variables de entorno (automático con render.yaml)
Render creará automáticamente:
- Base de datos PostgreSQL
- Variable `DATABASE_URL`
- Variable `SECRET_KEY` (generada)

Solo necesitas verificar:
- `DEBUG` = `False`
- `ALLOWED_HOSTS` (se configura automáticamente)

### 4. Después del primer despliegue
Crear superusuario desde el Shell de Render:
```bash
python manage.py createsuperuser
```

## 🎉 ¡Listo!

Tu aplicación estará disponible en: `https://southern-food-pos.onrender.com`

## Notas importantes:
- El primer despliegue puede tardar 5-10 minutos
- Plan gratuito: la app se "duerme" después de 15 min de inactividad
- Los archivos en `/media` no persisten (considera usar S3 o Cloudinary)
- Render redespliega automáticamente con cada push a main

## Solución rápida de problemas:
- **Error 500**: Revisa logs en Render dashboard
- **Base de datos**: Verifica que DATABASE_URL esté configurada
- **Estáticos no cargan**: Ejecuta `python manage.py collectstatic`
- **App no responde**: Verifica que gunicorn esté instalado
