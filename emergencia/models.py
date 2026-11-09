from django.db import models
from tutor.models import Usuario, Tutor  # Importa as dependências do app tutor


class ContatoEmergencia(models.Model):
    class Parentesco(models.TextChoices):
        PAI = 'Pai', 'Pai'
        MAE = 'Mãe', 'Mãe'
        FILHO_A = 'Filho(a)', 'Filho(a)'
        AMIGO_A = 'Amigo(a)', 'Amigo(a)'
        CONJUGE = 'Cônjuge', 'Cônjuge'
        OUTROS = 'Outros', 'Outros'

    pk = models.CompositePrimaryKey('id_contato', 'id_tutor')
    id_contato = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_contato')
    id_tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, db_column='id_tutor')
    parentesco = models.CharField(max_length=20, choices=Parentesco.choices)

    class Meta:
        db_table = 'contato_emergencia'
        managed = False