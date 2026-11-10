from django.db import models
from tutor.models import Cadastro

class ContatoEmergencia(models.Model):
    tutor = models.ForeignKey(Cadastro, on_delete=models.CASCADE, related_name='contatos_emergencia')

    nome = models.CharField(max_length=150, verbose_name="Nome")
    parentesco = models.CharField(max_length=50, verbose_name="Parentesco")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    email = models.EmailField(verbose_name="E-mail")

    principal = models.BooleanField(default=False, verbose_name="Contato de emergencia principal?")

    def __str__(self):
        return f"{self.nome} {self.parentesco} - Tutor: {self.tutor}"