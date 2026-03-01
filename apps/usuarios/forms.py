from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from .models import Usuario

class LoginForm(forms.Form):
    """
    Authentication form with email/password fields.
    Uses Tailwind CSS classes for consistent styling with the frontend.
    """
    email = forms.EmailField(
        max_length=254,
        validators=[validate_email],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Enter your password'
        })
    )

class RegistrationForm(UserCreationForm):
    """
    Extended user registration form that:
    - Uses email as username
    - Collects nombre_completo
    - Applies consistent form styling
    """
    email = forms.EmailField(
        max_length=254,
        validators=[validate_email],
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent transition-all',
            'placeholder': 'tu@email.com'
        })
    )
    nombre_completo = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent transition-all',
            'placeholder': 'Juan Pérez'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent transition-all',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent transition-all',
            'placeholder': 'Repite tu contraseña'
        }),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['email', 'nombre_completo', 'password1', 'password2']

    def save(self, commit=True):
        """Custom save method that ensures:
        - Email is properly saved (as it's used as username)
        - nombre_completo is saved
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nombre_completo = self.cleaned_data['nombre_completo']
        
        # Split nombre_completo into first_name and last_name if needed
        nombre_parts = self.cleaned_data['nombre_completo'].split(' ', 1)
        user.first_name = nombre_parts[0] if nombre_parts else ''
        user.last_name = nombre_parts[1] if len(nombre_parts) > 1 else ''
        
        if commit:
            user.save()
        return user