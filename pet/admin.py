from django.contrib import admin
from .models import (
    Pet,
    HistoricoLocalizacao,
    Clinica,
    Agendamento,
    Notificacao,
    PetTutor,
    TutorClinica,
)

admin.site.register(Pet)
admin.site.register(HistoricoLocalizacao)
admin.site.register(Clinica)
admin.site.register(Agendamento)
admin.site.register(Notificacao)
admin.site.register(PetTutor)
admin.site.register(TutorClinica)