from django import forms
from django.contrib.auth.hashers import make_password

from tutor.models import Usuario
from .models import ContatoEmergencia


class ContatoEmergenciaForm(forms.ModelForm):

    nome = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=120, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ContatoEmergencia
        fields = ['parentesco']
        widgets = {'parentesco': forms.Select(attrs={'class': 'form-control'})}

    field_order = ['nome', 'parentesco', 'telefone', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id_contato_id is not None:
            usuario = self.instance.id_contato
            for campo in ('nome', 'telefone', 'email'):
                self.fields[campo].initial = getattr(usuario, campo)
                self.fields[campo].disabled = True

    def save_para_tutor(self, tutor):
        """Cria (ou reaproveita, pelo e-mail) o Usuario e grava o contato de emergência."""
        if self.instance.id_contato_id is None:
            usuario, _ = Usuario.objects.get_or_create(
                email=self.cleaned_data['email'],
                defaults={
                    'nome': self.cleaned_data['nome'],
                    'telefone': self.cleaned_data['telefone'],
                    'senha_hash': make_password(None), 
                },
            )
            self.instance.id_contato = usuario
        self.instance.id_tutor = tutor
        self.instance.save()
        return self.instance