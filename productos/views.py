# productos/views.py
import json
from django.views.decorators.http import require_POST
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Producto, Categoria, MovimientoInventario
from .forms import ProductoForm, BusquedaProductoForm, MovimientoForm

def es_admin(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'admin'

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

# ==========================================
# PRODUCTOS
# ==========================================

@login_required
def producto_lista(request):
    form = BusquedaProductoForm(request.GET or None)
    productos = Producto.objects.filter(activo=True)
    
    if form.is_valid():
        busqueda = form.cleaned_data.get('busqueda')
        categoria = form.cleaned_data.get('categoria')
        
        if busqueda:
            productos = productos.filter(
                Q(nombre__icontains=busqueda) |
                Q(codigo_barras__icontains=busqueda)
            )
        
        if categoria:
            productos = productos.filter(categoria=categoria)
    
    # CAMBIADO AQUÍ: Modificamos el valor a 5 para mostrar máximo 5 productos por página
    paginator = Paginator(productos, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/lista.html', context)


# productos/views.py
@login_required
@user_passes_test(es_admin)
def producto_crear(request):
    codigo_precargado = request.GET.get('codigo', '')
    usar_escaner = request.GET.get('escaner', 'false') == 'true'
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # commit=False para manipular el objeto antes de guardarlo en base de datos
            producto = form.save(commit=False)
            producto.cantidad = 0  # El stock inicial siempre empieza en 0
            producto.save()
            
            messages.success(request, f'✅ Producto "{producto.nombre}" registrado exitosamente. (Stock inicial: 0)')
            
            if request.GET.get('from_scanner'):
                return redirect('productos:crear_escaner')
            return redirect('productos:lista')
    else:
        initial = {}
        if codigo_precargado:
            initial['codigo_barras'] = codigo_precargado
        form = ProductoForm(initial=initial)
    
    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Producto',
        'accion': 'Registrar',
        'codigo_precargado': codigo_precargado,
        'from_scanner': bool(request.GET.get('from_scanner')),
        'usar_escaner': usar_escaner,
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/form.html', context)


@login_required
@user_passes_test(es_admin)
def producto_crear_con_escaner(request):
    """Vista para registrar producto con escáner integrado"""
    context = get_user_context(request)
    return render(request, 'productos/form_escaner.html', context)


@login_required
@user_passes_test(es_admin)
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto_actualizado = form.save()
            messages.success(request, f'Producto "{producto_actualizado.nombre}" actualizado correctamente.')
            return redirect('productos:lista')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'titulo': 'Editar Producto',
        'accion': 'Actualizar',
        'producto': producto
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/form.html', context)


@login_required
@user_passes_test(es_admin)
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado correctamente.')
        return redirect('productos:lista')
    
    context = {
        'producto': producto
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/confirmar_eliminar.html', context)


@login_required
@user_passes_test(es_admin)
def entrada_crear(request):
    """Vista para registrar entrada de mercancía (individual o por lote)"""
    
    if request.method == 'POST':
        # Verificar si es una entrada individual o por lote
        producto_id = request.POST.get('producto_id')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion', '')
        
        # Si es entrada individual
        if producto_id and cantidad:
            try:
                producto = Producto.objects.get(id=producto_id, activo=True)
                cantidad = int(cantidad)
                
                if cantidad <= 0:
                    messages.error(request, 'La cantidad debe ser mayor a 0')
                    return redirect('productos:entrada')
                
                # Actualizar stock
                producto.cantidad = F('cantidad') + cantidad
                producto.save()
                
                # Registrar movimiento
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo='entrada',
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    total=producto.precio * cantidad,
                    descripcion=descripcion or f'Entrada de {cantidad} unidades de {producto.nombre}',
                    usuario=request.user
                )
                
                messages.success(request, f'✅ Entrada de {cantidad} unidades de "{producto.nombre}" registrada exitosamente.')
                return redirect('productos:movimientos')
                
            except Producto.DoesNotExist:
                messages.error(request, 'Producto no encontrado')
            except ValueError:
                messages.error(request, 'Cantidad inválida')
        
        # Si es entrada por lote (desde el carrito)
        elif request.POST.get('entrada_lote') == 'true':
            try:
                items = json.loads(request.POST.get('items', '[]'))
                
                if not items:
                    messages.error(request, 'No hay productos en la lista')
                    return redirect('productos:entrada')
                
                with transaction.atomic():
                    for item in items:
                        producto = Producto.objects.get(id=item['id'], activo=True)
                        cantidad = int(item['cantidad'])
                        
                        producto.cantidad = F('cantidad') + cantidad
                        producto.save()
                        
                        MovimientoInventario.objects.create(
                            producto=producto,
                            tipo='entrada',
                            cantidad=cantidad,
                            precio_unitario=producto.precio,
                            total=producto.precio * cantidad,
                            descripcion=item.get('descripcion', f'Entrada de {cantidad} unidades de {producto.nombre}'),
                            usuario=request.user
                        )
                
                messages.success(request, f'✅ Entrada de {len(items)} productos registrada exitosamente.')
                return redirect('productos:movimientos')
                
            except json.JSONDecodeError:
                messages.error(request, 'Error al procesar los datos')
            except Producto.DoesNotExist:
                messages.error(request, 'Producto no encontrado en la lista')
            except Exception as e:
                messages.error(request, f'Error al procesar: {str(e)}')
    
    # GET - Mostrar formulario
    context = {
        'productos': Producto.objects.filter(activo=True).order_by('nombre'),
        'categorias': Categoria.objects.all().order_by('nombre'),
        'titulo': 'Registrar Entrada de Mercancía'
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/entrada_form.html', context)


@login_required
@user_passes_test(es_admin)
def movimiento_lista(request):
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').all()
    
    tipo = request.GET.get('tipo')
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    
    paginator = Paginator(movimientos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipos': MovimientoInventario.TIPO_MOVIMIENTO
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/movimientos.html', context)


@login_required
def productos_stock_bajo(request):
    productos_bajos = Producto.objects.filter(
        activo=True,
        cantidad__lte=F('cantidad_minima')
    ).order_by('cantidad')
    
    context = {
        'productos_bajos': productos_bajos,
        'total_bajos': productos_bajos.count()
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/stock_bajo.html', context)


@login_required
def producto_buscar_api(request):
    termino = request.GET.get('q', '')
    productos = Producto.objects.filter(
        Q(nombre__icontains=termino) |
        Q(codigo_barras__icontains=termino),
        activo=True,
        cantidad__gt=0
    )[:10]
    
    data = [{
        'id': p.id,
        'nombre': p.nombre,
        'codigo_barras': p.codigo_barras or 'N/A',
        'precio': str(p.precio),
        'cantidad': p.cantidad
    } for p in productos]
    
    return JsonResponse(data, safe=False)


# ==========================================
# CRUD DE CATEGORÍAS
# ==========================================

@login_required
@user_passes_test(es_admin)
def categoria_lista(request):
    categorias = Categoria.objects.all().order_by('nombre')
    context = {
        'categorias': categorias
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/categoria_lista.html', context)


@login_required
@user_passes_test(es_admin)
def categoria_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, f'Categoría "{nombre}" creada exitosamente.')
            return redirect('productos:categoria_lista')
    
    context = {
        'titulo': 'Crear Categoría',
        'accion': 'Crear'
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/categoria_form.html', context)


@login_required
@user_passes_test(es_admin)
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        if nombre:
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            categoria.save()
            messages.success(request, f'Categoría "{nombre}" actualizada correctamente.')
            return redirect('productos:categoria_lista')
    
    context = {
        'categoria': categoria,
        'titulo': 'Editar Categoría',
        'accion': 'Actualizar'
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/categoria_form.html', context)


@login_required
@user_passes_test(es_admin)
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
        return redirect('productos:categoria_lista')
    
    context = {
        'categoria': categoria
    }
    context.update(get_user_context(request))
    
    return render(request, 'productos/categoria_confirmar_eliminar.html', context)


# ==========================================
# API DE CÓDIGO DE BARRAS
# ==========================================

# productos/views.py

@login_required
def producto_buscar_barcode(request):
    """API para buscar producto por código de barras"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({
            'success': False,
            'message': 'Código de barras vacío'
        })
    
    try:
        # Buscamos el producto
        producto = Producto.objects.get(codigo_barras=codigo, activo=True)
        
        # Preparamos los datos incluyendo el nuevo formato
        data = {
            'success': True,
            'exists': True, # Bandera explícita para el frontend
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'precio': str(producto.precio),
            'cantidad': producto.cantidad,
            'categoria_nombre': producto.categoria.nombre if producto.categoria else 'Sin categoría',
            # Nuevos campos solicitados en el formulario
            'formato': getattr(producto, 'formato', 'Pieza Individual'), 
            'piezas_por_caja': getattr(producto, 'piezas_por_caja', 1),
        }
    except Producto.DoesNotExist:
        # Si no existe, devolvemos success: True pero exists: False para manejarlo en el frontend
        data = {
            'success': True,
            'exists': False,
            'codigo': codigo,
            'message': f'Producto con código "{codigo}" no encontrado'
        }
    
    return JsonResponse(data)

@login_required
@user_passes_test(es_admin)
def producto_escaner_registro(request):
    """Vista del escáner de código de barras para registrar productos"""
    context = get_user_context(request)
    return render(request, 'productos/escaner_registro.html', context)


# Modifica esta función en tu productos/views.py para incluir formato y piezas por caja:

@login_required
@user_passes_test(es_admin)
def producto_buscar_por_codigo(request):
    """API para buscar producto por código (para el escáner de registro)"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({
            'success': False,
            'message': 'Código de barras vacío'
        })
    
    try:
        producto = Producto.objects.get(codigo_barras=codigo, activo=True)
        data = {
            'success': True,
            'exists': True,
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'precio': str(producto.precio),
            'cantidad': producto.cantidad,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria.id if producto.categoria else None,
            'categoria_nombre': producto.categoria.nombre if producto.categoria else 'Sin categoría',
            'cantidad_minima': producto.cantidad_minima,
            'formato': producto.formato,                      # <-- AGREGADO
            'piezas_por_caja': producto.piezas_por_caja,      # <-- AGREGADO
            'tiene_imagen': bool(producto.imagen)
        }
    except Producto.DoesNotExist:
        data = {
            'success': True,
            'exists': False,
            'codigo': codigo,
            'message': f'El producto con código "{codigo}" no existe. Puedes registrarlo.'
        }

    return JsonResponse(data)

# ==========================================
# PROCESAMIENTO DE ENTRADAS MASIVAS (LOTE)
# ==========================================

@login_required
@user_passes_test(es_admin)
@require_POST
def guardar_entrada_lote_api(request):
    """
    API para procesar una lista de entradas de mercancía de forma masiva (carrito).
    """
    try:
        data = json.loads(request.body)
        items = data.get('productos', [])
        
        if not items:
            return JsonResponse({'success': False, 'message': 'La lista de productos está vacía.'}, status=400)
        
        with transaction.atomic():
            for item in items:
                producto = get_object_or_404(Producto, id=item['id'])
                cantidad_unidades = int(item['piezas_equivalentes'])
                formato = item['formato']
                cantidad_solicitada = item['cantidad']
                
                if formato == 'lote':
                    descripcion_mov = f"Entrada por lote: {cantidad_solicitada} caja(s) de {item['piezas_por_caja']} pzas. {item.get('descripcion', '')}"
                else:
                    descripcion_mov = f"Entrada individual: {cantidad_solicitada} pzas. {item.get('descripcion', '')}"
                
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo='entrada',
                    cantidad=cantidad_unidades,
                    precio_unitario=producto.precio,
                    total=producto.precio * cantidad_unidades,
                    descripcion=descripcion_mov[:200],
                    usuario=request.user
                )
                
                producto.cantidad = F('cantidad') + cantidad_unidades
                producto.save()
                
        return JsonResponse({'success': True, 'message': 'Entradas registradas y procesadas con éxito.'})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Formato JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error en el servidor: {str(e)}'}, status=500)
    
