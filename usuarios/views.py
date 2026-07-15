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

# usuarios/views.py

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # ==========================================
    # CREDENCIALES HARCODEADAS (SOLO DESARROLLO)
    # ==========================================
    HARDCORE_USERS = {
        'superinventix': {
            'password': 'Solo/leveling/br50.',
            'first_name': 'Super',
            'last_name': 'Inventix',
            'is_superuser': True,
            'is_staff': True,
            'rol': 'admin'
        },
        'adminTIX': {
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'TIX',
            'is_superuser': False,
            'is_staff': False,
            'rol': 'admin'
        },
        'cajero1': {
            'password': 'cajero123',
            'first_name': 'Carlos',
            'last_name': 'Ramírez',
            'is_superuser': False,
            'is_staff': False,
            'rol': 'empleado'
        }
    }
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 1. VERIFICAR CREDENCIALES HARCODEADAS
        if username in HARDCORE_USERS:
            user_data = HARDCORE_USERS[username]
            if password == user_data['password']:
                # CREAR USUARIO EN LA BASE DE DATOS SI NO EXISTE
                from django.contrib.auth.models import User
                from usuarios.models import PerfilUsuario
                
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'email': f'{username}@inventix.com',
                        'is_superuser': user_data['is_superuser'],
                        'is_staff': user_data['is_staff'],
                    }
                )
                
                # Si el usuario existe, actualizar permisos
                if not created:
                    user.is_superuser = user_data['is_superuser']
                    user.is_staff = user_data['is_staff']
                    user.save()
                
                # Crear/actualizar perfil
                perfil, _ = PerfilUsuario.objects.get_or_create(
                    usuario=user,
                    defaults={'rol': user_data['rol']}
                )
                if not _:
                    perfil.rol = user_data['rol']
                    perfil.save()
                
                # Iniciar sesión
                from django.contrib.auth import login
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                return redirect('dashboard:home')
        
        # 2. INTENTAR AUTENTICACIÓN NORMAL (BD)
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f'¡Bienvenido {username}!')
            return redirect('dashboard:home')
        
        # 3. ERROR
        messages.error(request, 'Usuario o contraseña incorrectos')
        return render(request, 'usuarios/login.html', {'form': LoginForm()})
    
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('login')


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def crear_superusuario_secreto(request):
    """Ruta secreta para crear superusuario (SOLO PARA DESARROLLO)"""
    clave_secreta = request.GET.get('key', '')
    
    if clave_secreta != 'inventix2026':
        return JsonResponse({'error': 'Clave incorrecta'}, status=403)
    
    try:
        from django.contrib.auth.models import User
        
        username = request.GET.get('username', 'superinventix')
        password = request.GET.get('password', 'Solo/leveling/br50.')
        email = request.GET.get('email', 'super@inventix.com')
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'mensaje': f'El usuario {username} ya existe',
                'existe': True
            })
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        return JsonResponse({
            'mensaje': f'✅ Superusuario {username} creado exitosamente',
            'creado': True,
            'usuario': username,
            'password': password
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)