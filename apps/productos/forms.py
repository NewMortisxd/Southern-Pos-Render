from django import forms
from .models import Producto, Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        
class ProductoForm(forms.ModelForm):
    # Campos adicionales para controlar los checkboxes
    no_imagen = forms.BooleanField(required=False)
    no_codigo = forms.BooleanField(required=False)
    
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'precio', 'stock', 'imagen', 'codigo_barras']
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
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
        
    def clean(self):
        cleaned_data = super().clean()
        no_imagen = cleaned_data.get('no_imagen')
        imagen = cleaned_data.get('imagen')
        
        # Si se seleccionó 'no tiene imagen' pero no hay imagen actual
        # y tampoco se subió una nueva, no hay problema
        if no_imagen and not imagen and not (self.instance and self.instance.imagen):
            # Aquí se podría asignar una imagen por defecto si es necesario
            pass
        
        return cleaned_data