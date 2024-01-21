from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps

def manager_required(login_url=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url or 'login')
            if not request.user.groups.filter(name='Managers').exists():
                raise PermissionDenied  # Odmowa dostępu, jeśli użytkownik nie jest w grupie "Managers"
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def non_manager_required(login_url=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url or 'login')
            if request.user.groups.filter(name='Managers').exists():
                raise PermissionDenied  # Odmowa dostępu, jeśli użytkownik jest w grupie "Managers"
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator