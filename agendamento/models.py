from django.db import models
from tutor.models import Usuario, Tutor
from clinica.models import Clinica
from pet.models import Pet

class Agendamento(models.Model):
    # Tabela `agendamento`
    id_agendamento = models.AutoField(primary_key=True)
    id_tutor = models.ForeignKey(Tutor, on_delete = models.RESTRICT, db_column = 'id_tutor')
    id_coleira = models.ForeignKey(Pet, on_delete = models.RESTRICT, db_column = 'id_coleira')
    id_clinica = models.ForeignKey(Clinica, on_delete = models.RESTRICT, db_column = 'id_clinica')
    data_hora = models.DateTimeField()

    class Meta:
        db_table = 'agendamento'
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields = ['id_clinica', 'data_hora'],
                name = 'uq_agendamento_clinica_data_hora',
            ),
        ]

    def __str__(self):
        return f"{self.id_coleira} @ {self.id_clinica} - {self.data_hora}"