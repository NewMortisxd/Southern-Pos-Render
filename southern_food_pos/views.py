# In southern_food_pos/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

# Then in urls.py
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # ... rest of your URLs
]