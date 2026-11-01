from django import forms
from .models import Usuario


class CadastroForm(forms.ModelForm):
    # Senha entra como texto puro no form e vira hash na view (coluna senha_hash)
    senha = forms.CharField(max_length = 128, widget = forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']
        # Validação de requisito minimo de senha
    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        if len(senha) < 8:
            raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres")
        return senha