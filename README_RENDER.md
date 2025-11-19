# Despliegue en Render

Este proyecto está configurado para desplegarse automáticamente en Render.

## Pasos para desplegar:

### 1. Preparar el repositorio

Asegúrate de que todos los archivos estén en tu repositorio Git:
- `build.sh` - Script de construcción
- `render.yaml` - Configuración de Render
- `requirements.txt` - Dependencias de Python
- `.gitignore` - Archivos a ignorar

### 2. Crear cuenta en Render

1. Ve a [render.com](https://render.com) y crea una cuenta
2. Conecta tu cuenta de GitHub/GitLab/Bitbucket

### 3. Desplegar desde el Dashboard

#### Opción A: Usando render.yaml (Recomendado)

1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "Blueprint"
3. Conecta tu repositorio
4. Render detectará automáticamente el archivo `render.yaml`
5. Haz clic en "Apply"

#### Opción B: Configuración manual

1. En el dashboard de Render, haz clic en "New +" → "Web Service"
2. Conecta tu repositorio
3. Configura los siguientes valores:
   - **Name**: southern-food-pos
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn southern_food_pos.wsgi:application`
   - **Instance Type**: Free (o el que prefieras)

4. Crea una base de datos PostgreSQL:
   - Ve a "New +" → "PostgreSQL"
   - **Name**: southern-food-pos-db
   - Copia la "Internal Database URL"

5. Agrega las variables de entorno en tu Web Service:
   - `DATABASE_URL`: (pega la URL de la base de datos)
   - `SECRET_KEY`: (genera una clave secreta segura)
   - `DEBUG`: `False`
   - `PYTHON_VERSION`: `3.11.0`

### 4. Variables de entorno importantes

Render configurará automáticamente:
- `RENDER_EXTERNAL_HOSTNAME` - El dominio de tu aplicación
- `DATABASE_URL` - La URL de conexión a PostgreSQL

Debes configurar manualmente:
- `SECRET_KEY` - Genera una con: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DEBUG` - Debe ser `False` en producción

### 5. Permisos del script de build

Si tienes problemas con permisos, ejecuta localmente:
```bash
chmod +x build.sh
git add build.sh
git commit -m "Add execute permission to build.sh"
git push
```

### 6. Migraciones y superusuario

Después del primer despliegue, necesitarás crear un superusuario:

1. Ve a tu servicio en Render
2. Haz clic en "Shell" en el menú lateral
3. Ejecuta:
```bash
python manage.py createsuperuser
```

### 7. Archivos estáticos

Los archivos estáticos se sirven automáticamente con WhiteNoise. No necesitas configuración adicional.

### 8. Archivos media (uploads)

Para archivos subidos por usuarios en producción, considera usar:
- AWS S3
- Cloudinary
- Render Disks (persistente)

Por defecto, los archivos en `/media` se perderán en cada despliegue.

## Solución de problemas

### Error: "Application failed to respond"
- Verifica que `gunicorn` esté en `requirements.txt`
- Revisa los logs en el dashboard de Render

### Error de base de datos
- Verifica que `DATABASE_URL` esté configurada correctamente
- Asegúrate de que las migraciones se ejecutaron

### Archivos estáticos no cargan
- Verifica que `whitenoise` esté en `requirements.txt`
- Revisa que `STATIC_ROOT` esté configurado correctamente

### Error 500
- Cambia temporalmente `DEBUG=True` para ver el error
- Revisa los logs en Render
- Verifica que `ALLOWED_HOSTS` incluya tu dominio de Render

## Comandos útiles

Ejecutar migraciones manualmente:
```bash
python manage.py migrate
```

Recolectar archivos estáticos:
```bash
python manage.py collectstatic --no-input
```

Ver logs en tiempo real:
```bash
# Desde el dashboard de Render, ve a "Logs"
```

## Actualizaciones

Render desplegará automáticamente cuando hagas push a tu rama principal:
```bash
git add .
git commit -m "Update application"
git push origin main
```

## Notas importantes

- El plan gratuito de Render puede tener tiempos de inicio lentos (cold starts)
- La base de datos gratuita tiene límites de almacenamiento
- Los archivos en `/media` no persisten entre despliegues (usa almacenamiento externo)
