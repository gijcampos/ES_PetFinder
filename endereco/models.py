from django.db import models
from .models import Cadastro

class Endereco(models.Model):
    cep = models.CharField(max_length=9)
    rua = models.CharField(max_length=255)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=125)
    bairro = models.CharField(max_length=125)
    cidade = models.CharField(max_length=125)
    estado = models.CharField(max_length=125)

def __str__(self):
    return self.nome