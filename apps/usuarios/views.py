from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, RegistrationForm
from django.http import JsonResponse
from .models import Usuario, Business  # Add Business import
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Use email to authenticate instead of username
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect('dashboard')  # Changed from 'home' to 'dashboard'
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user but don't save to database yet
            user = form.save(commit=False)
            
            # If username is not provided, use email as username
            if not user.username:
                user.username = user.email
                
            # Now save the user
            user.save()
            
            # Save many-to-many relationships if any
            form.save_m2m()
            
            # Create or update business profile
            business, created = Business.objects.get_or_create(user=user)
            business.nombre_negocio = request.POST.get('nombre_negocio', '')
            business.direccion_negocio = request.POST.get('direccion_negocio', '')
            business.telefono_negocio = request.POST.get('telefono_negocio', '')
            business.ruc_negocio = request.POST.get('ruc_negocio', '')
            business.email_negocio = request.POST.get('email_negocio', '')
            business.save()
            
            # Log the user in after registration
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')  # Changed to redirect to dashboard
        else:
            # Form is not valid, errors will be displayed
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'usuarios/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('login')

# Add the missing check_email view function
def check_email(request):
    """
    AJAX endpoint to check if an email already exists in the database.
    Returns JSON response with 'exists' field indicating if the email exists.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '')
        exists = Usuario.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def dashboard_view(request):
    """
    View for the main dashboard page
    """
    return render(request, 'dashboard.html')