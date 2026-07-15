# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuario_lista, name='lista'),
    path('crear/', views.usuario_crear, name='crear'),
    path('editar/<int:pk>/', views.usuario_editar, name='editar'),
    path('eliminar/<int:pk>/', views.usuario_eliminar, name='eliminar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]