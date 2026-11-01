from django import forms
from .models import Pet

#formularios dos Pets

class PetsForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            'id_coleira',
            'nome',
            'especie',
            'raca',
            'idade',
            'id_tutor'
        ]