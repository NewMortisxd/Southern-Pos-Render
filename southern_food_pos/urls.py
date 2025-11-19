from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from core import views

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
    path('', TemplateView.as_view(template_name='landing.html'), name='landing_page'),
    # Make sure you have this in your URL patterns
    path('login/', views.login_view, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

# Añadir manejo de archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
