# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from productos.models import Producto, MovimientoInventario, Categoria
from ventas.models import Venta
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

# dashboard/views.py - Agregar es_admin al contexto

@login_required
def home(request):
    # ==========================================
    # DETERMINAR EL ROL DEL USUARIO
    # ==========================================
    es_super = request.user.is_superuser
    es_admin = hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin'
    es_empleado = hasattr(request.user, 'perfil') and request.user.perfil.rol == 'empleado'
    
    # ==========================================
    # CONTEXTO BÁSICO PARA TODOS (INCLUYE es_admin)
    # ==========================================
    context = {
        'es_super': es_super,
        'es_admin': es_admin,  # <--- IMPORTANTE: esto va al template
        'es_empleado': es_empleado,
        'username': request.user.username,
        'rol': request.user.perfil.get_rol_display() if hasattr(request.user, 'perfil') else 'Superusuario'
    }
    
    hoy = timezone.now().date()
    total_productos = Producto.objects.filter(activo=True).count()
    
    # ==========================================
    # PRODUCTOS CON STOCK BAJO (PARA TODOS)
    # ==========================================
    productos_bajos = Producto.objects.filter(
        activo=True,
        cantidad__lte=5
    )
    total_bajos = productos_bajos.count()
    
    # ==========================================
    # DASHBOARD PARA SUPERUSUARIO (superinventix)
    # ==========================================
    if es_super:
        # Estadísticas completas del sistema
        context.update({
            'total_productos': total_productos,
            'productos_bajos': productos_bajos[:5],
            'total_bajos': total_bajos,
            'total_categorias': Categoria.objects.count(),
            'total_usuarios': User.objects.count(),
            'total_ventas': Venta.objects.count(),
            'total_movimientos': MovimientoInventario.objects.count(),
            
            # Ventas del día
            'ventas_hoy': Venta.objects.filter(fecha__date=hoy).count(),
            'total_ventas_hoy': Venta.objects.filter(fecha__date=hoy).aggregate(
                total=Sum('total')
            )['total'] or 0,
            
            # Movimientos recientes
            'movimientos_recientes': MovimientoInventario.objects.select_related(
                'producto', 'usuario'
            ).order_by('-fecha')[:10],
            
            # Productos más vendidos
            'productos_mas_vendidos': MovimientoInventario.objects.filter(
                tipo='venta',
                fecha__gte=timezone.now() - timedelta(days=30)
            ).values('producto__nombre').annotate(
                total_vendido=Sum('cantidad')
            ).order_by('-total_vendido')[:5],
            
            # Categorías con más productos
            'categorias_populares': Categoria.objects.annotate(
                num_productos=Count('producto')
            ).order_by('-num_productos')[:5],
            
            # Ventas por mes (últimos 6 meses)
            'ventas_por_mes': [
                {
                    'mes': (timezone.now() - timedelta(days=30*i)).strftime('%B %Y'),
                    'total': float(Venta.objects.filter(
                        fecha__month=(timezone.now() - timedelta(days=30*i)).month,
                        fecha__year=(timezone.now() - timedelta(days=30*i)).year
                    ).aggregate(total=Sum('total'))['total'] or 0)
                }
                for i in range(6)
            ],
            
            'mostrar_dashboard_super': True,
            'mostrar_dashboard_admin': False,
            'mostrar_dashboard_empleado': False,
        })
    
    # ==========================================
    # DASHBOARD PARA ADMINISTRADOR (adminTIX)
    # ==========================================
    elif es_admin:
        # Estadísticas del negocio (sin acceso a configuración del sistema)
        productos_disponibles = Producto.objects.filter(activo=True, cantidad__gt=0).count()
        
        context.update({
            'total_productos': total_productos,
            'productos_disponibles': productos_disponibles,
            'productos_bajos': productos_bajos[:5],
            'total_bajos': total_bajos,
            'total_categorias': Categoria.objects.count(),
            'total_usuarios_negocio': User.objects.filter(is_superuser=False).count(),
            
            # Ventas del día
            'ventas_hoy': Venta.objects.filter(fecha__date=hoy).count(),
            'total_ventas_hoy': Venta.objects.filter(fecha__date=hoy).aggregate(
                total=Sum('total')
            )['total'] or 0,
            
            # Movimientos recientes
            'movimientos_recientes': MovimientoInventario.objects.select_related(
                'producto', 'usuario'
            ).order_by('-fecha')[:10],
            
            # Productos más vendidos
            'productos_mas_vendidos': MovimientoInventario.objects.filter(
                tipo='venta',
                fecha__gte=timezone.now() - timedelta(days=30)
            ).values('producto__nombre').annotate(
                total_vendido=Sum('cantidad')
            ).order_by('-total_vendido')[:5],
            
            # Categorías con más productos
            'categorias_populares': Categoria.objects.annotate(
                num_productos=Count('producto')
            ).order_by('-num_productos')[:5],
            
            # Ventas por mes
            'ventas_por_mes': [
                {
                    'mes': (timezone.now() - timedelta(days=30*i)).strftime('%B %Y'),
                    'total': float(Venta.objects.filter(
                        fecha__month=(timezone.now() - timedelta(days=30*i)).month,
                        fecha__year=(timezone.now() - timedelta(days=30*i)).year
                    ).aggregate(total=Sum('total'))['total'] or 0)
                }
                for i in range(6)
            ],
            
            'mostrar_dashboard_super': False,
            'mostrar_dashboard_admin': True,
            'mostrar_dashboard_empleado': False,
        })
    
    # ==========================================
    # DASHBOARD PARA EMPLEADO/CAJERO (cajero1)
    # ==========================================
    else:
        # Estadísticas del empleado
        productos_disponibles = Producto.objects.filter(activo=True, cantidad__gt=0).count()
        
        # Ventas del empleado hoy
        ventas_hoy = Venta.objects.filter(
            usuario=request.user,
            fecha__date=hoy
        ).count()
        
        total_ventas_hoy = Venta.objects.filter(
            usuario=request.user,
            fecha__date=hoy
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Últimas ventas del empleado
        ultimas_ventas = Venta.objects.filter(
            usuario=request.user
        ).order_by('-fecha')[:5]
        
        context.update({
            'total_productos': total_productos,
            'productos_disponibles': productos_disponibles,
            'productos_stock_bajo': productos_bajos[:5],
            'total_stock_bajo': total_bajos,
            'ventas_hoy': ventas_hoy,
            'total_ventas_hoy': total_ventas_hoy,
            'ultimas_ventas': ultimas_ventas,
            'total_ventas_mes': Venta.objects.filter(
                usuario=request.user,
                fecha__month=hoy.month,
                fecha__year=hoy.year
            ).count(),
            
            'mostrar_dashboard_super': False,
            'mostrar_dashboard_admin': False,
            'mostrar_dashboard_empleado': True,
        })
    
    return render(request, 'dashboard/home.html', context)