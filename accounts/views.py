from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .decorators import role_required

from django.shortcuts import redirect

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth.models import User

from django.http import HttpResponse

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Tu cuenta ha sido activada. Ahora puedes iniciar sesión.')
        return redirect('accounts:login')
    else:
        return HttpResponse('El enlace de activación no es válido o ha expirado.')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Desactiva la cuenta hasta confirmar email
            user.save()

            # --- Enviar correo de activación ---
            current_site = get_current_site(request)
            subject = 'Activa tu cuenta'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email = EmailMessage(subject, message, to=[user.email])
            email.send()

            messages.info(request, "Te hemos enviado un enlace de activación a tu correo.")
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})



def error_403(request, exception=None):
    messages.error(request, "No tienes permiso para acceder a esta sección.")
    return render(request, 'accounts/403.html', status=403)


def dashboard_redirect(request):
    """
    Redirige al dashboard correspondiente según el rol del usuario.
    """
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return redirect('accounts:admin_dashboard')
        elif request.user.groups.filter(name='Teacher').exists():
            return redirect('accounts:teacher_dashboard')
        elif request.user.groups.filter(name='User').exists():
            return redirect('accounts:user_dashboard')
    # Si no tiene rol o no está logueado
    return redirect('accounts:login')

def home(request):
    return render(request, 'accounts/home.html')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard_base.html')

@login_required
@role_required('Teacher','Admin')
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()       # Obtiene el usuario validado
            login(request, user)         # Inicia la sesión
            messages.success(request, f"Bienvenido {user.username}")
            return redirect('accounts:profile')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)                    # Cierra sesión
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('accounts:login')  # Redirige al login

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('accounts:profile')
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)
    context = {'uform': uform, 'pform': pform}
    return render(request, 'accounts/profile_edit.html', context)
