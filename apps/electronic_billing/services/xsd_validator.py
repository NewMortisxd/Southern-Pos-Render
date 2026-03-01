"""
Validador de XML contra XSD oficial del SRI Ecuador
"""
from lxml import etree
import os


XSD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "schemas", "factura_V1.1.0.xsd"
)


def validate_invoice_xml(xml_bytes: bytes) -> tuple:
    """
    Valida xml_bytes contra el XSD oficial del SRI.
    
    Args:
        xml_bytes: XML en formato bytes UTF-8
        
    Returns:
        tuple: (is_valid: bool, errors: list[dict])
        Cada error: {'linea': int, 'columna': int, 'mensaje': str, 'tipo': 'error'|'warning'}
    """
    try:
        # Cargar el XSD
        if not os.path.exists(XSD_PATH):
            return False, [{
                "linea": 0,
                "columna": 0,
                "mensaje": f"No se encontró el archivo XSD en: {XSD_PATH}",
                "tipo": "error"
            }]
        
        with open(XSD_PATH, "rb") as f:
            xsd_doc = etree.parse(f)
        
        schema = etree.XMLSchema(xsd_doc)
        
        # Parsear el XML
        doc = etree.fromstring(xml_bytes)
        
        # Validar
        is_valid = schema.validate(doc)
        
        # Extraer errores
        errors = []
        for e in schema.error_log:
            error_dict = {
                "linea": e.line if e.line else 0,
                "columna": e.column if e.column else 0,
                "mensaje": e.message,
                "tipo": "error" if e.level_name in ("ERROR", "FATAL") else "warning"
            }
            errors.append(error_dict)
        
        return is_valid, errors
        
    except etree.XMLSyntaxError as e:
        return False, [{
            "linea": getattr(e, 'lineno', 0),
            "columna": 0,
            "mensaje": f"Error de sintaxis XML: {str(e)}",
            "tipo": "error"
        }]
    except Exception as e:
        return False, [{
            "linea": 0,
            "columna": 0,
            "mensaje": f"Error inesperado: {str(e)}",
            "tipo": "error"
        }]
