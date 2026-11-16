from django import forms
from .models import Pet, PetTutor


class PetsForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['id_coleira', 'nome', 'especie', 'raca', 'idade']

    def __init__(self, *args, tutor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tutor = tutor

    def save(self, commit=True):
        pet = super().save(commit)
        if commit and self.tutor is not None:
            PetTutor.objects.get_or_create(id_coleira=pet, id_tutor=self.tutor)
        return pet