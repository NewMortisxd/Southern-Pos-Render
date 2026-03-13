from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.static import serve
from core import views
from apps.usuarios import views as usuarios_views  # Importar vistas de usuarios
import os

def custom_logout(request):
    logout(request)
    return redirect('/accounts/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.usuarios.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('productos/', include('apps.productos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('configuraciones/', include(('apps.configuraciones.urls', 'configuraciones'), namespace='configuraciones')),
    path('clients/', include(('apps.clients.urls', 'clients'), namespace='clients')),
    path('transacciones/', include(('apps.transacciones.urls', 'transacciones'), namespace='transacciones')),
    path('kds/', include(('apps.ventas.urls_kds', 'kds'), namespace='kds')),
    path('electronic/', include(('apps.electronic_billing.urls', 'electronic_billing'), namespace='electronic_billing')),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing_page'),
    # Make sure you have this in your URL patterns
    path('login/', views.login_view, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', usuarios_views.register_view, name='register'),  # Usar vista de usuarios
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test-logo/', TemplateView.as_view(template_name='test_logo.html'), name='test_logo'),
    # Favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.svg', permanent=True)),
]

# Servir archivos media en desarrollo y producción
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Servir archivos estáticos solo en desarrollo (WhiteNoise maneja producción)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Handlers de error personalizados
handler404 = 'southern_food_pos.views.error_404'
handler500 = 'southern_food_pos.views.error_500'
handler403 = 'southern_food_pos.views.error_403'
handler400 = 'southern_food_pos.views.error_400'
