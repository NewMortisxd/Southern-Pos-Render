# 🚀 Instalación Rápida - Laboratorio de Facturación Electrónica

## Pasos de Instalación

### 1. Instalar Dependencias

```bash
pip install lxml>=4.9.0
```

### 2. Verificar Configuración

La app ya está agregada a `INSTALLED_APPS` en `settings.py`:
```python
'apps.electronic_billing',
```

Las URLs ya están configuradas en `urls.py`:
```python
path('electronic/', include(('apps.electronic_billing.urls', 'electronic_billing'), namespace='electronic_billing')),
```

### 3. Verificar Estructura de Archivos

Asegúrate de que existan estos archivos:
```
schemas/
└── factura_V1.1.0.xsd

apps/electronic_billing/
├── __init__.py
├── apps.py
├── urls.py
├── views_lab.py
├── services/
│   ├── __init__.py
│   ├── xml_generator.py
│   └── xsd_validator.py
└── templates/
    └── lab/
        └── xml_lab.html
```

### 4. Ejecutar el Servidor

```bash
python manage.py runserver
```

### 5. Acceder al Laboratorio

Abre tu navegador en:
```
http://localhost:8000/electronic/lab/
```

## ✅ Verificación

1. Deberías ver una página con diseño dark mode
2. Un dropdown con las últimas 50 ventas
3. Al seleccionar una venta y presionar "Generar y Validar XML":
   - Se genera el XML
   - Se valida contra el XSD
   - Se muestra el resultado con badge de estado

## 🔧 Troubleshooting

### Error: ModuleNotFoundError: No module named 'lxml'
```bash
pip install lxml
```

### Error: No se encontró el archivo XSD
Verifica que existe `schemas/factura_V1.1.0.xsd` en la raíz del proyecto.

### Error: TemplateDoesNotExist
Verifica que existe `apps/electronic_billing/templates/lab/xml_lab.html`

### Error: No reverse match for 'xml_lab'
Verifica que las URLs estén correctamente configuradas en `urls.py`

## 📝 Notas

- El laboratorio requiere que existan ventas en la base de datos
- Si no hay ventas, el dropdown estará vacío
- Puedes crear ventas de prueba desde el módulo de ventas del sistema

## 🎯 Próximos Pasos

Una vez que el laboratorio funcione correctamente:
1. Verifica que los XMLs generados sean válidos
2. Ajusta los datos de prueba en `xml_generator.py` según tu negocio
3. Implementa la firma digital (fase 2)
4. Implementa el envío al SRI (fase 3)
