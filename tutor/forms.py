from django import forms
from .models import Cadastro

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Cadastro
        fields = [
            'nome',
            'email',
            'telefone',
            'senha'
        ]
        widgets = {
            'senha':forms.PasswordInput(),
        }

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        if len(senha) < 8:
            raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres")
        return senha