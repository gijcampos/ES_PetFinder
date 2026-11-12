from django.db import models
from tutor.models import Tutor, Usuario
from pet.models import Pet

class Notificacao(models.Model):
    class Tipo(models.TextChoices):
        SAIDA_RAIO = 'SAIDA_RAIO', 'SAIDA_RAIO'
        AVISO_CONTATO = 'AVISO_CONTATO', 'AVISO_CONTATO'

    id_notificacao = models.BigAutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE, db_column = 'id_usuario')
    id_tutor_origem = models.ForeignKey(Tutor, on_delete = models.RESTRICT, db_column = 'id_tutor_origem')
    id_coleira = models.ForeignKey(Pet, on_delete = models.RESTRICT, db_column = 'id_coleira', blank = True, null = True)
    tipo = models.CharField(max_length = 20, choices = Tipo.choices)
    data_hora = models.DateTimeField()
    mensagem = models.CharField(max_length = 255)
    lida = models.BooleanField(default = False)

    class Meta:
        db_table = 'notificacao'
        managed = False

    def __str__(self):
        return f"{self.tipo} para {self.id_usuario} @ {self.data_hora}"