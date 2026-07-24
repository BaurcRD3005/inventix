# productos/urls.py
from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.producto_lista, name='lista'),
    path('crear/', views.producto_crear, name='crear'),
    path('editar/<int:pk>/', views.producto_editar, name='editar'),
    path('eliminar/<int:pk>/', views.producto_eliminar, name='eliminar'),
    
    # Ruta de entrada con ambos nombres para evitar el NoReverseMatch
    path('entrada/', views.entrada_crear, name='entrada'), 
    path('entrada/', views.entrada_crear, name='entrada_form'), # <--- Agregamos este alias
    path('api/guardar-entrada-lote/', views.guardar_entrada_lote_api, name='guardar_entrada_lote_api'),
    
    path('movimientos/', views.movimiento_lista, name='movimientos'),
    path('stock-bajo/', views.productos_stock_bajo, name='stock_bajo'),
    path('api/buscar/', views.producto_buscar_api, name='buscar_api'),
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    path('categorias/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),
    path('categorias/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),
    path('api/buscar-barcode/', views.producto_buscar_barcode, name='buscar_barcode'),
    path('escaner-registro/', views.producto_escaner_registro, name='escaner_registro'),
    path('api/buscar-por-codigo/', views.producto_buscar_por_codigo, name='buscar_por_codigo'),
    path('crear-escaner/', views.producto_crear_con_escaner, name='crear_escaner'),
]