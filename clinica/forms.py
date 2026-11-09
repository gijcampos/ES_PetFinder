from django import forms
from .models import Clinica

class ClinicaForm(forms.ModelForm):
    class Meta:
        model = Clinica
        fields = [
            'nome', 
            'endereco', 
            'telefone', 
            'horario_funcionamento', 
            'preferida'
            ]

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Clinica Vet'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Rua, N° - Bairro, Cidade'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(41) 9999-9999'}),
            'horario_funcionamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Seg a Sex das 08h às 18h'}),
            'preferida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }