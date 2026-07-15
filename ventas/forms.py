# ventas/forms.py
from django import forms
from .models import Venta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Observaciones de la venta...',
                'class': 'form-control'
            }),
        }