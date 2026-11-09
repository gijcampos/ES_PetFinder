from django.db import models
from tutor.models import Cadastro 

class Clinica(models.Model):
    tutor = models.ForeignKey(Cadastro, on_delete=models.CASCADE, related_name='clinicas')
    
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    horario_funcionamento = models.CharField(max_length=100, blank=True, null=True)
    preferida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} ({'Preferida' if self.preferida else 'Normal'})"