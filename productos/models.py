# productos/models.py
from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# productos/models.py

class Producto(models.Model):
    TIPO_FORMATO = (
        ('pieza', 'Pieza Individual'),
        ('lote', 'Caja / Lote'),
    )

    codigo_barras = models.CharField('Código de Barras', max_length=100, unique=True, blank=True, null=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Manejo de Formato e Inventario
    formato = models.CharField('Formato de venta', max_length=10, choices=TIPO_FORMATO, default='pieza')
    piezas_por_caja = models.PositiveIntegerField('Piezas por Caja/Lote', default=1, 
                                                 help_text="Si es por lote, especifica cuántas piezas individuales contiene.")
    
    cantidad = models.IntegerField('Cantidad disponible', default=0)
    cantidad_minima = models.IntegerField('Cantidad mínima', default=5)
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)
    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)
    activo = models.BooleanField('Activo', default=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        formato_str = "Lote" if self.formato == 'lote' else "Pieza"
        return f"{self.nombre} ({formato_str}) - {self.codigo_barras or 'Sin código'}"
    
    def stock_bajo(self):
        return self.cantidad <= self.cantidad_minima

    @property
    def total_cajas_disponibles(self):
        """Calcula el equivalente de stock actual en formato caja/lote"""
        if self.formato == 'lote' and self.piezas_por_caja > 1:
            return self.cantidad / self.piezas_por_caja
        return self.cantidad

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada de Mercancía'),
        ('venta', 'Venta'),
        ('ajuste', 'Ajuste de Inventario'),
    )
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField('Cantidad')
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, null=True, blank=True)
    descripcion = models.CharField('Descripción', max_length=200, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} - {self.cantidad}"