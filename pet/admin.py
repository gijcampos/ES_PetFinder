from django.contrib import admin
from .models import (
    Pet,
    HistoricoLocalizacao,
    Agendamento
)

admin.site.register(Pet)
admin.site.register(HistoricoLocalizacao)
admin.site.register(Agendamento)