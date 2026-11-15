from django.contrib import admin
from .models import Pet, HistoricoLocalizacao, PetTutor

admin.site.register(Pet)
admin.site.register(HistoricoLocalizacao)
admin.site.register(PetTutor)