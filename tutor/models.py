from django.db import models


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(
        max_length=120,
        unique=True,
        error_messages={'unique': "Erro: Este e-mail ja está sendo usado!"},
    )
    telefone = models.CharField(max_length=11)
    senha_hash = models.CharField(max_length=255)

    class Meta:
        db_table = 'usuario'
        managed = False
        
    def __str__(self):
        return self.nome


class Tutor(models.Model):
    id_tutor = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='id_tutor',
    )

    class Meta:
        db_table = 'tutor'
        managed = False

    def __str__(self):
        return self.id_tutor.nome