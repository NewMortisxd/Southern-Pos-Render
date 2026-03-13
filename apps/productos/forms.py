from django import forms
from .models import Producto, Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        
class ProductoForm(forms.ModelForm):
    # Campo adicional para controlar el checkbox de imagen
    no_imagen = forms.BooleanField(required=False)
    
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'tipo_producto', 'descripcion', 
            'precio_base', 'incluye_iva', 'costo', 
            'controla_stock', 'stock', 'stock_minimo', 'unidad_medida',
            'codigo_barras', 'sku', 'imagen'
        ]
    
    def clean_stock(self):
        controla_stock = self.cleaned_data.get('controla_stock')
        stock = self.cleaned_data.get('stock')
        
        # Si no controla stock, retornar None
        if not controla_stock:
            return None
        
        # Si controla stock, el stock es requerido
        if controla_stock and stock is None:
            raise forms.ValidationError("El stock es requerido cuando se controla inventario.")
        
        return stock
    
    def clean_codigo_barras(self):
        codigo_barras = self.cleaned_data.get('codigo_barras')
        no_codigo = self.cleaned_data.get('no_codigo', False)
        
        # Si marcaron "no tiene código", retornar None
        if no_codigo:
            return None
            
        # Si el código de barras está vacío, retornar None
        if not codigo_barras:
            return None
            
        # Verificar si ya existe un producto con este código (excepto el actual)
        queryset = Producto.objects.filter(codigo_barras=codigo_barras)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise forms.ValidationError("Ya existe un producto con este código de barras.")
            
        return codigo_barras
    
    def clean_sku(self):
        """Validar SKU único si se proporciona"""
        sku = self.cleaned_data.get('sku')
        
        # Si no se proporciona, se generará automáticamente en el modelo
        if not sku:
            return ''  # Retornar string vacío para que el modelo lo genere
        
        # Si se proporciona, verificar que sea único
        queryset = Producto.objects.filter(sku=sku)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError("Ya existe un producto con este SKU.")
        
        return sku

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Guardar el usuario para usarlo en clean()
        self.user = user
        
        # Si estamos editando, mostrar el precio final (con IVA) en el campo
        # para que sea consistente con lo que se ve en la lista
        if self.instance and self.instance.pk:
            from decimal import Decimal
            # Calcular el precio final para mostrarlo
            precio_final = self.instance.precio  # Usa la propiedad que calcula precio con IVA
            self.initial['precio_base'] = float(precio_final)
        
        # Filtrar categorías por el usuario actual
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario_creador=user)
            # Cambiar el texto del campo vacío y hacerlo requerido
            self.fields['categoria'].empty_label = "Seleccionar categoría"
            self.fields['categoria'].required = True
            # Eliminar la opción vacía si hay categorías disponibles
            if self.fields['categoria'].queryset.exists():
                self.fields['categoria'].empty_label = None
            
        # Hacer opcional el campo imagen
        self.fields['imagen'].required = False
        
        # Hacer que el campo código de barras sea opcional
        self.fields['codigo_barras'].required = False
        
        # Hacer que el campo costo sea opcional
        self.fields['costo'].required = False
        
        # Hacer que el campo SKU sea opcional (se genera automáticamente si no se proporciona)
        self.fields['sku'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        no_imagen = cleaned_data.get('no_imagen')
        imagen = cleaned_data.get('imagen')
        
        # Manejo de precio e IVA
        precio_ingresado = cleaned_data.get('precio_base')
        incluye_iva = cleaned_data.get('incluye_iva')
        
        if precio_ingresado:
            from decimal import Decimal, ROUND_HALF_UP
            from apps.usuarios.models import Business
            
            iva_porcentaje = Decimal('15')  # Default
            try:
                if hasattr(self, 'user') and self.user:
                    business = Business.objects.filter(user=self.user).first()
                    if business and business.iva_porcentaje:
                        iva_porcentaje = business.iva_porcentaje
            except:
                pass
            
            # SIEMPRE tratamos el precio ingresado como precio final con IVA
            # y calculamos el precio_base
            precio_con_iva = precio_ingresado
            precio_base_calculado = precio_con_iva / (Decimal('1') + iva_porcentaje / Decimal('100'))
            cleaned_data['precio_base'] = precio_base_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            # Siempre marcar incluye_iva como True
            cleaned_data['incluye_iva'] = True
        
        # Si se seleccionó 'no tiene imagen' pero no hay imagen actual
        # y tampoco se subió una nueva, no hay problema
        if no_imagen and not imagen and not (self.instance and self.instance.imagen):
            pass
        
        return cleaned_data