from django import forms
from .models import Endereco

# Formulário dos Endereços

class EndForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = [
            'CEP',
            'rua',
            'logradouro',
            'numero',
            'bairro',
            'cidade',
            'estado'
        ]

# Função de Verificação de Endereço Inválido