from django import forms
from .models import Cliente

# Formulario para crear o editar un cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['codigo', 'nombre', 'razon_social', 'identificacion', 'email', 
                  'telefono', 'direccion', 'ciudad', 'grupo', 'credito', 'estado',
                  'cupo', 'tasa_descuento', 'tasa_recargo', 'comentarios']
        widgets = {
            # Campo Código
            'codigo': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese el código...'
            }),
            # Campo Nombre
            'nombre': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese el nombre...'
            }),
            # Campo Razón Social
            'razon_social': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese la razón social...'
            }),
            # Campo Identificación
            'identificacion': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese la cédula o RUC...'
            }),
            # Campo Email
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese el email...'
            }),
            # Campo Teléfono
            'telefono': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese el teléfono...'
            }),
            # Campo Dirección
            'direccion': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese la dirección...'
            }),
            # Campo Ciudad
            'ciudad': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese la ciudad...'
            }),
            # Campo Grupo
            'grupo': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
            }),
            # Campo Crédito
            'credito': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese los días de crédito...'
            }),
            # Campo Estado
            'estado': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
            }),
            # Campo Cupo
            'cupo': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese el cupo...',
                'step': '0.01'
            }),
            # Campo Tasa de Descuento
            'tasa_descuento': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese la tasa de descuento...',
                'step': '0.01'
            }),
            # Campo Tasa de Recargo
            'tasa_recargo': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese la tasa de recargo...',
                'step': '0.01'
            }),
            # Campo Comentarios
            'comentarios': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-3 min-h-[120px] focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all',
                'placeholder': 'Ingrese comentarios adicionales sobre el cliente...'
            }),
        }