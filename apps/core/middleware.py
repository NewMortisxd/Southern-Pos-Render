from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        # Middleware de inicialización estándar en Django
        self.get_response = get_response

    def __call__(self, request):
        # Lógica principal del middleware antes/después de la vista
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Verifica si el usuario no está autenticado y trata de acceder a una ruta restringida
        # Si es así, lo redirige a la página de inicio (landing_page)
        if not request.user.is_authenticated and request.path not in [reverse('login'), reverse('register'), '/']:
            return redirect('landing_page')
        return None  # Permite el acceso si está autenticado o es una ruta permitida
