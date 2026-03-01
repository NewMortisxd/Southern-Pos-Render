from django.urls import path
from .views_lab import xml_lab_view

app_name = 'electronic_billing'

urlpatterns = [
    path('lab/', xml_lab_view, name='xml_lab'),
]
