from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .decorators import role_required

from django.shortcuts import redirect

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
@role_required('Teacher')
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')

def register_view(request):
    if request.method == 'POST':                      # Si el usuario envía el formulario
        form = RegisterForm(request.POST)             # Carga los datos del POST
        if form.is_valid():                           # Valida los campos
            user = form.save()                        # Guarda el usuario (crea User)
            messages.success(request, "Cuenta creada correctamente. Ahora inicia sesión.")
            return redirect('accounts:login')         # Redirige al login
    else:
        form = RegisterForm()                         # Si entra por primera vez, form vacío
    return render(request, 'accounts/register.html', {'form': form})

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
