from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
def group_required(group_name):
    """Devuelve un decorador que permite solo usuarios de cierto grupo"""
    def in_group(user):
        return user.is_authenticated and user.groups.filter(name=group_name).exists()
    return user_passes_test(in_group)


def login_required_no_next(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Redirigir directamente al login sin next
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
