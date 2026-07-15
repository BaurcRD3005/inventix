# ventas/models.py
from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

class Venta(models.Model):
    folio = models.CharField('Folio', max_length=20, unique=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField('Fecha de venta', auto_now_add=True)
    observaciones = models.TextField('Observaciones', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Venta {self.folio} - ${self.total}"
    
    def save(self, *args, **kwargs):
        if not self.folio:
            from datetime import datetime
            fecha = datetime.now().strftime('%Y%m%d')
            ultima_venta = Venta.objects.filter(folio__startswith=f'V{fecha}').order_by('-folio').first()
            if ultima_venta:
                numero = int(ultima_venta.folio[9:]) + 1
            else:
                numero = 1
            self.folio = f'V{fecha}{numero:04d}'
        super().save(*args, **kwargs)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField('Cantidad')
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def __str__(self):
        return f"{self.venta.folio} - {self.producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)