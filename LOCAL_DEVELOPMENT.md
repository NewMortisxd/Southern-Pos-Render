# Desarrollo Local

## Configuración inicial

### 1. Crear entorno virtual
```bash
python -m venv venv
```

### 2. Activar entorno virtual

Windows (CMD):
```bash
venv\Scripts\activate
```

Windows (PowerShell):
```bash
venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear archivo .env
Copia `.env.example` a `.env` y configura:
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Recolectar archivos estáticos
```bash
python manage.py collectstatic
```

### 8. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

## Comandos útiles

### Crear nueva migración
```bash
python manage.py makemigrations
```

### Ver SQL de migraciones
```bash
python manage.py sqlmigrate app_name migration_number
```

### Abrir shell de Django
```bash
python manage.py shell
```

### Ejecutar tests
```bash
python manage.py test
```

### Limpiar base de datos
```bash
python manage.py flush
```

### Crear app nueva
```bash
python manage.py startapp nombre_app apps/nombre_app
```

## Probar con Gunicorn localmente

```bash
gunicorn southern_food_pos.wsgi:application -c gunicorn_config.py
```

## Base de datos

### PostgreSQL local
Si quieres usar PostgreSQL localmente:

1. Instalar PostgreSQL
2. Crear base de datos:
```sql
CREATE DATABASE southern_food_pos;
CREATE USER southern_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE southern_food_pos TO southern_user;
```

3. Actualizar .env:
```env
DATABASE_URL=postgresql://southern_user:password@localhost:5432/southern_food_pos
```

### SQLite (alternativa simple)
Para desarrollo rápido, puedes usar SQLite modificando settings.py temporalmente:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Troubleshooting

### Error: No module named 'decouple'
```bash
pip install python-decouple
```

### Error: No module named 'psycopg2'
```bash
pip install psycopg2-binary
```

### Error: Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Resetear migraciones
```bash
# Eliminar archivos de migración (excepto __init__.py)
# Eliminar base de datos
python manage.py makemigrations
python manage.py migrate
```
