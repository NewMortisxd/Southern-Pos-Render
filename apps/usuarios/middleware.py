from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for the admin site
        if request.path.startswith('/admin/'):
            # If user is not authenticated, redirect to custom login
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)
            # If user is authenticated but not staff/superuser, redirect to dashboard
            elif not request.user.is_staff and not request.user.is_superuser:
                return redirect('dashboard')
        
        response = self.get_response(request)
        return response