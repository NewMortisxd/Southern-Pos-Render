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
    - Collects first/last name
    - Applies consistent form styling
    - Automatically generates full_name
    """
    email = forms.EmailField(
        max_length=254,
        validators=[validate_email],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Enter your last name'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Enter your password'
        }),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-emerald-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Confirm your password'
        }),
        label="Confirm Password"
    )

    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        """Custom save method that ensures:
        - Email is properly saved (as it's used as username)
        - Full name is automatically generated
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Set email explicitly
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Generate full name if model supports it
        if hasattr(user, 'nombre_completo'):
            user.nombre_completo = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
        
        if commit:
            user.save()
        return user