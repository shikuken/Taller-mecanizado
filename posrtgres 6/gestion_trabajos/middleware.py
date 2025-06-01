from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import re

class LoginRequiredMiddleware:
    """
    Middleware que requiere que el usuario esté autenticado para acceder a cualquier vista,
    excepto las especificadas en LOGIN_REQUIRED_URLS_EXCEPTIONS.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.required = True
        self.exceptions = getattr(settings, 'LOGIN_REQUIRED_URLS_EXCEPTIONS', [])
        self.exceptions.append(reverse('login'))
        
    def __call__(self, request):
        if self.required:
            if not request.user.is_authenticated:
                path = request.path_info.lstrip('/')
                if not any(re.match(pattern, request.path_info) for pattern in self.exceptions):
                    return redirect('login')
        
        response = self.get_response(request)
        return response
