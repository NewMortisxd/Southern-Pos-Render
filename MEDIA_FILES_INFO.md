# ⚠️ Archivos Media en Render

## Problema Actual

Los archivos subidos por usuarios (imágenes de productos) en `/media/` **NO persisten** en Render con el plan gratuito. 

Cada vez que redespliegas, se pierden todos los archivos subidos.

## Soluciones

### 1. Cloudinary (Recomendado - GRATIS)

Cloudinary ofrece 25GB gratis y es perfecto para imágenes de productos.

**Pasos:**
1. Crear cuenta en https://cloudinary.com
2. Instalar: `pip install django-cloudinary-storage`
3. Configurar en `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
    # ...
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'tu_cloud_name',
    'API_KEY': 'tu_api_key',
    'API_SECRET': 'tu_api_secret'
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### 2. AWS S3

Más complejo pero muy escalable.

**Pasos:**
1. Crear bucket en AWS S3
2. Instalar: `pip install django-storages boto3`
3. Configurar en `settings.py`

### 3. Render Disks (Requiere plan de pago)

Render ofrece discos persistentes pero requiere upgrade del plan gratuito.

**Costo:** Desde $7/mes

## Solución Temporal

Por ahora, las imágenes de productos solo funcionarán:
- En desarrollo local
- Hasta el próximo redespliegue en Render

Para producción real, **debes usar Cloudinary o S3**.

## Estado Actual

✅ Archivos estáticos (`/static/`) - Funcionan con WhiteNoise
❌ Archivos media (`/media/`) - Se pierden en cada despliegue

## Próximos Pasos

1. Decidir entre Cloudinary (más fácil) o S3 (más control)
2. Configurar el servicio elegido
3. Actualizar `settings.py` y `requirements.txt`
4. Redesplegar en Render
