# ventas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import F, Sum
from django.http import JsonResponse
from .models import Venta, DetalleVenta
from productos.models import Producto, MovimientoInventario
from .forms import VentaForm
from datetime import datetime

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

@login_required
def venta_crear(request):
    producto_id = request.GET.get('producto')  # Para escáner
    
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.usuario = request.user
                venta.save()
                
                productos_ids = request.POST.getlist('producto_id[]')
                cantidades = request.POST.getlist('cantidad[]')
                precios = request.POST.getlist('precio[]')
                
                subtotal_total = 0
                
                for i in range(len(productos_ids)):
                    if productos_ids[i] and cantidades[i] and precios[i]:
                        producto = Producto.objects.get(id=productos_ids[i])
                        cantidad = int(cantidades[i])
                        precio = float(precios[i])
                        subtotal = cantidad * precio
                        subtotal_total += subtotal
                        
                        DetalleVenta.objects.create(
                            venta=venta,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=subtotal
                        )
                        
                        producto.cantidad = F('cantidad') - cantidad
                        producto.save()
                        
                        MovimientoInventario.objects.create(
                            producto=producto,
                            tipo='venta',
                            cantidad=-cantidad,
                            precio_unitario=precio,
                            total=subtotal,
                            descripcion=f'Venta {venta.folio}',
                            usuario=request.user
                        )
                
                venta.subtotal = subtotal_total
                venta.total = subtotal_total
                venta.save()
                
                messages.success(request, f'✅ Venta {venta.folio} registrada exitosamente.')
                return redirect('ventas:detalle', pk=venta.id)
    else:
        form = VentaForm()
    
    producto_seleccionado = None
    if producto_id:
        try:
            producto_seleccionado = Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            pass
    
    context = {
        'form': form,
        'productos': Producto.objects.filter(activo=True, cantidad__gt=0),
        'producto_seleccionado': producto_seleccionado,
    }
    context.update(get_user_context(request))
    
    return render(request, 'ventas/crear.html', context)


@login_required
def venta_lista(request):
    ventas = Venta.objects.select_related('usuario').all().order_by('-fecha')
    
    paginator = Paginator(ventas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    context.update(get_user_context(request))
    
    return render(request, 'ventas/lista.html', context)


@login_required
def venta_detalle(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.select_related('producto').all()
    
    context = {
        'venta': venta,
        'detalles': detalles
    }
    context.update(get_user_context(request))
    
    return render(request, 'ventas/detalle.html', context)


@login_required
def venta_escaner(request):
    """Vista del escáner de código de barras"""
    context = get_user_context(request)
    return render(request, 'ventas/crear_barcode.html', context)


@login_required
def venta_buscar_producto_api(request):
    """API para buscar producto por código de barras desde el escáner"""
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
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'precio': str(producto.precio),
            'cantidad': producto.cantidad,
            'descripcion': producto.descripcion or 'Sin descripción',
            'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría'
        }
    except Producto.DoesNotExist:
        data = {
            'success': False,
            'message': f'Producto con código "{codigo}" no encontrado',
            'codigo': codigo
        }
    
    return JsonResponse(data)


@login_required
def venta_agregar_producto_api(request):
    """API para agregar producto a la venta desde el escáner"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))
    
    if not producto_id:
        return JsonResponse({'success': False, 'message': 'ID de producto requerido'})
    
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
        
        if producto.cantidad < cantidad:
            return JsonResponse({
                'success': False,
                'message': f'Stock insuficiente. Disponible: {producto.cantidad}'
            })
        
        data = {
            'success': True,
            'message': f'Producto "{producto.nombre}" agregado a la venta',
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': cantidad,
                'subtotal': str(producto.precio * cantidad)
            }
        }
        return JsonResponse(data)
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        })
        
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from .models import Venta

# Esta línea protege la vista para que solo el Superusuario pueda ejecutar la eliminación
@user_passes_test(lambda u: u.is_superuser)
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    return redirect('ventas:lista') # Asegúrate de que este nombre coincida con tu urls.py

# ventas/views.py - Agregar al final

@login_required
def venta_buscar_por_qr(request):
    """API para buscar producto por código QR en ventas"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({
            'success': False,
            'message': 'Código QR vacío'
        })
    
    try:
        producto = Producto.objects.get(codigo_barras=codigo, activo=True)
        
        if producto.cantidad <= 0:
            return JsonResponse({
                'success': False,
                'message': f'Producto "{producto.nombre}" sin stock disponible'
            })
        
        data = {
            'success': True,
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'precio': float(producto.precio),
            'cantidad': producto.cantidad,
            'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
            'imagen_url': producto.imagen.url if producto.imagen else None
        }
    except Producto.DoesNotExist:
        data = {
            'success': False,
            'message': f'No se encontró producto con código: {codigo}'
        }
    
    return JsonResponse(data)