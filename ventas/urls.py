# ventas/urls.py
from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('crear/', views.venta_crear, name='crear'),
    path('lista/', views.venta_lista, name='lista'),
    path('detalle/<int:pk>/', views.venta_detalle, name='detalle'),
    path('escaner/', views.venta_escaner, name='escaner'),
    path('api/buscar-producto/', views.venta_buscar_producto_api, name='buscar_producto_api'),
    path('api/agregar-producto/', views.venta_agregar_producto_api, name='agregar_producto_api'),
    path('eliminar/<int:venta_id>/', views.eliminar_venta, name='eliminar'),
    path('api/buscar-qr/', views.venta_buscar_por_qr, name='buscar_qr'),
]