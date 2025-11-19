from django.contrib import admin
from .models import BusinessConfiguration

@admin.register(BusinessConfiguration)
class BusinessConfigurationAdmin(admin.ModelAdmin):
    list_display = ('nombre_negocio', 'user', 'telefono_negocio', 'email_negocio')
    search_fields = ('nombre_negocio', 'user__username', 'email_negocio')
