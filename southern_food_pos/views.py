"""
Vistas de error personalizadas para el proyecto
"""
from django.shortcuts import render


def error_404(request, exception):
    """Vista personalizada para error 404"""
    return render(request, '404.html', status=404)


def error_500(request):
    """Vista personalizada para error 500"""
    return render(request, '500.html', status=500)


def error_403(request, exception):
    """Vista personalizada para error 403"""
    return render(request, '403.html', status=403)


def error_400(request, exception):
    """Vista personalizada para error 400"""
    return render(request, '400.html', status=400)
