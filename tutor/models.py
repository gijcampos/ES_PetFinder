from django.db import models

class Cadastro(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True, error_messages={'unique': "Erro: Este e-mail já esta sendo usado!"})
    telefone = models.CharField(max_length=128)
    senha = models.CharField(max_length=128)


def __str__(self):
    return self.nome