from django.contrib import admin
from .models import Usuario, Tutor
from endereco.models import Endereco

admin.site.register(Usuario)
admin.site.register(Tutor)
admin.site.register(Endereco)