from django.contrib import messages
from django.shortcuts import redirect

def role_required(*roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated and (user.groups.filter(name__in=roles).exists() or user.is_superuser):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect('accounts:error_403')  # o cualquier vista pública
        return _wrapped_view
    return decorator
