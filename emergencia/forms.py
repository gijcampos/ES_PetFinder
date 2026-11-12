from django import forms
from .models import ContatoEmergencia

class ContatoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContatoEmergencia
        fields = [
            'id_contato',
            'parentesco',
        ]
        widgets = {
            'id_contato': forms.Select(attrs={'class': 'form-control'}),
            'parentesco': forms.Select(attrs={'class': 'form-control'}),
        }