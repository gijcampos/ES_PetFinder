from django import forms
from .models import ContatoEmergencia

class ContatoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContatoEmergencia
        fields = [
            'nome',
            'parentesco',
            'telefone',
            'email',
            'principal'
        ]

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # Botão de Sim/Não, você pode customiza-lo
            'principal': forms.RadioSelect(choices=[(True, 'Sim'), (False, 'Não')])
        }