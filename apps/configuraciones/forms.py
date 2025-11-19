from django import forms
from apps.usuarios.models import Business

class BusinessSettingsForm(forms.ModelForm):
    
    # Add these as non-model fields if you still want them in your form
    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50',
            'placeholder': 'Ciudad'
        })
    )
    MODO_OPERACION_CHOICES = [
        ('restaurante', 'Modo Restaurante'),
        ('retail', 'Modo Retail/Supermercado'),
    ]
    modo_operacion = forms.ChoiceField(
        choices=MODO_OPERACION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'hidden'}),
        required=True
    )
    logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
        })
    )
    
    class Meta:
        model = Business
        fields = [
            'nombre_negocio', 
            'direccion_negocio',
            'telefono_negocio', 
            'email_negocio',
            'ruc_negocio',
            'iva_porcentaje',
            'moneda',
            'mostrar_logo_en_factura',
            'mensaje_factura',
            'politica_devolucion',
            'modo_operacion',
        ]
        widgets = {
            'nombre_negocio': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': 'Nombre del negocio'}),
            'direccion_negocio': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': 'Dirección del negocio'}),
            'telefono_negocio': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': 'Teléfono'}),
            'email_negocio': forms.EmailInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': 'Email'}),
            'ruc_negocio': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': 'RUC'}),
            'iva_porcentaje': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': '15', 'min': '0', 'max': '100', 'step': '0.01'}),
            'moneda': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': '$'}),
            'mostrar_logo_en_factura': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-emerald-600 focus:ring-emerald-500'}),
            'mensaje_factura': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': '¡Gracias por su compra!'}),
            'politica_devolucion': forms.TextInput(attrs={'class': 'w-full rounded-lg border-2 border-gray-400 bg-white p-2 focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50', 'placeholder': 'Para devoluciones, presente este comprobante dentro de los próximos 7 días.'}),
        }
