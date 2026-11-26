from django import forms
from tutor.models import Tutor
from .models import Pet, PetTutor

class PetsForm(forms.ModelForm):
    tutor = forms.ModelChoiceField(queryset = Tutor.objects.all())

    class Meta:
        model = Pet
        fields = ['id_coleira', 'nome', 'especie', 'raca', 'idade']

    def save(self, commit = True):
        pet = super().save(commit)
        if commit:
            PetTutor.objects.get_or_create(id_coleira = pet, id_tutor = self.cleaned_data['tutor'])
        return pet