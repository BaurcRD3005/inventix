# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    )
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField('Rol', max_length=20, choices=ROLES, default='empleado')
    telefono = models.CharField('Teléfono', max_length=15, blank=True, null=True)
    direccion = models.TextField('Dirección', blank=True, null=True)
    fecha_contratacion = models.DateField('Fecha de contratación', auto_now_add=True)
    activo = models.BooleanField('Activo', default=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"