from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    def check(user):
        if user.is_authenticated and (user.groups.filter(name__in=roles).exists() or user.is_superuser):
            return True
        raise PermissionDenied
    return user_passes_test(check)
