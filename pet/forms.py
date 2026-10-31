from django import forms
from .models import Pet

#formularios dos Pets

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            'nome',
            'especie',
            'raca',
            'idade',
            'id_disp_rastreamento',
            'tutor'
        ]