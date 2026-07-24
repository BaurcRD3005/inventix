# productos/forms.py
from django import forms
from .models import Producto, Categoria, MovimientoInventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # 'cantidad' ha sido removido de aquí para que el stock inicial siempre comience en 0
        fields = [
            'codigo_barras', 
            'nombre', 
            'descripcion', 
            'precio', 
            'categoria', 
            'formato', 
            'piezas_por_caja', 
            'cantidad_minima', 
            'imagen'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'formato': forms.Select(attrs={'class': 'form-select'}),
            'piezas_por_caja': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'cantidad_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class BusquedaProductoForm(forms.Form):
    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o código de barras',
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'cantidad', 'descripcion']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Abastecimiento mensual'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)