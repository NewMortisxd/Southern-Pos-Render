"""
Vista del laboratorio de facturación electrónica.
Permite seleccionar una venta, generar su XML y validarlo contra el XSD del SRI.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.ventas.models import Venta
from .services.xml_generator import InvoiceXMLGenerator
from .services.xsd_validator import validate_invoice_xml


@login_required
def xml_lab_view(request):
    """
    Vista principal del laboratorio de XML.
    
    GET: Muestra el formulario con las últimas 50 ventas
    POST: Genera y valida el XML de la venta seleccionada
    """
    context = {}
    
    if request.method == "POST":
        sale_id = request.POST.get("sale_id")
        
        if sale_id:
            try:
                # Obtener la venta con sus relaciones
                sale = get_object_or_404(
                    Venta.objects.select_related('cliente', 'usuario_creador')
                                 .prefetch_related('detalleventa_set__producto'),
                    id=sale_id
                )
                
                # Generar el XML
                print("\n🔄 Generando XML...")
                generator = InvoiceXMLGenerator(sale)
                xml_data = generator.generate()  # devuelve bytes UTF-8
                
                # Validar contra el XSD
                is_valid, errors = validate_invoice_xml(xml_data)
                
                # Preparar contexto
                context["xml"] = xml_data.decode("utf-8")
                context["is_valid"] = is_valid
                context["errors"] = errors or []
                context["selected_sale_id"] = int(sale_id)
                context["sale"] = sale
                
            except ValueError as e:
                # Error de configuración (ej: porcentaje de IVA inválido)
                context["error"] = str(e)
            except Venta.DoesNotExist:
                context["error"] = f"No se encontró la venta con ID {sale_id}"
            except Exception as e:
                context["error"] = f"Error al procesar la venta: {str(e)}"
    
    # Obtener las últimas 50 ventas para el dropdown
    context["sales"] = Venta.objects.select_related('cliente').order_by('-id')[:50]
    
    return render(request, 'lab/xml_lab.html', context)
