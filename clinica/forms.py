from django import forms
from .models import Clinica

class ClinicaForm(forms.ModelForm):
    preferida = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    horario_funcionamento = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Seg a Sex das 08h às 18h'})
    )

    class Meta:
        model = Clinica
        fields = [
            'nome', 
            'endereco', 
            'telefone', 
        ]

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Clinica Vet'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Rua, N° - Bairro, Cidade'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(41) 9999-9999'}),
        }