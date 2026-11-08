from django import forms
from django.core.exceptions import ValidationError
from .models import Endereco
import requests

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

def clean_CEP(self):
        cep = self.cleaned_data.get('CEP')
        # Limpa o CEP para ter apenas números
        cep_formatado = ''.join(filter(str.isdigit, str(cep)))

        if len(cep_formatado) != 8:
            raise ValidationError("O CEP deve conter 8 dígitos válidos.")

        # Validação extra via API no backend para garantir que o CEP existe
        resposta = requests.get(f'https://viacep.com.br/ws/{cep_formatado}/json/')
        if resposta.status_code == 200:
            dados = resposta.json()
            if 'erro' in dados or 'error' in dados:
                raise ValidationError("Endereço inválido. O CEP informado não existe.")
        
        return cep_formatado