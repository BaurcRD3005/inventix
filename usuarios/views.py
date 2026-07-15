# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from .models import PerfilUsuario
from .forms import RegistroUsuarioForm, LoginForm, UsuarioUpdateForm, PerfilUsuarioForm
from productos.views import es_admin

# ==========================================
# FUNCIÓN AUXILIAR PARA CONTEXTO
# ==========================================
def get_user_context(request):
    """Obtiene el contexto del usuario para los templates"""
    return {
        'es_admin': hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin',
        'es_super': request.user.is_superuser,
        'es_empleado': hasattr(request.user, 'perfil') and request.user.perfil.rol == 'empleado',
    }

@user_passes_test(es_admin)
def usuario_crear(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
            return redirect('usuarios:lista')
    else:
        form = RegistroUsuarioForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Usuario',
        'accion': 'Crear'
    }
    context.update(get_user_context(request))
    
    return render(request, 'usuarios/form.html', context)

@user_passes_test(es_admin)
def usuario_lista(request):
    usuarios = User.objects.select_related('perfil').all()
    context = {
        'usuarios': usuarios
    }
    context.update(get_user_context(request))
    
    return render(request, 'usuarios/lista.html', context)

@user_passes_test(es_admin)
def usuario_editar(request, pk):
    user = get_object_or_404(User, pk=pk)
    perfil = user.perfil
    
    if request.method == 'POST':
        user_form = UsuarioUpdateForm(request.POST, instance=user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, f'Usuario "{user.username}" actualizado correctamente.')
            return redirect('usuarios:lista')
    else:
        user_form = UsuarioUpdateForm(instance=user)
        perfil_form = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'titulo': f'Editar Usuario: {user.username}',
        'accion': 'Actualizar'
    }
    context.update(get_user_context(request))
    
    return render(request, 'usuarios/form.html', context)

@user_passes_test(es_admin)
def usuario_eliminar(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if user == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('usuarios:lista')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario "{username}" eliminado correctamente.')
        return redirect('usuarios:lista')
    
    context = {
        'user': user
    }
    context.update(get_user_context(request))
    
    return render(request, 'usuarios/confirmar_eliminar.html', context)

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('login')