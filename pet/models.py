from django.db import models
from tutor.models import Tutor, Usuario


class Pet(models.Model):
    # Tabela `pet`: o id da coleira e a chave primaria
    id_coleira = models.CharField(max_length = 9, primary_key = True)
    # Sem ON DELETE no SQL, logo o padrao e RESTRICT
    nome = models.CharField(max_length = 60)
    especie = models.CharField(max_length = 30, blank = True, null = True)
    raca = models.CharField(max_length = 50, blank = True, null = True)
    # TINYINT UNSIGNED
    idade = models.PositiveSmallIntegerField(blank = True, null = True)

    class Meta:
        db_table = 'pet'
        managed = False

    def __str__(self):
        return f"{self.nome} ({self.especie})"


class HistoricoLocalizacao(models.Model):
    # Tabela `historico_localizacao`
    id_localizacao = models.BigAutoField(primary_key=True)
    id_coleira = models.ForeignKey(Pet, on_delete = models.CASCADE, db_column = 'id_coleira')
    data_hora = models.DateTimeField()
    latitude = models.DecimalField(max_digits = 9, decimal_places = 6)
    longitude = models.DecimalField(max_digits = 9, decimal_places = 6)

    class Meta:
        db_table = 'historico_localizacao'
        managed = False
        indexes = [
            models.Index(fields = ['id_coleira', 'data_hora']),
        ]

    def __str__(self):
        return f"{self.id_coleira_id} @ {self.data_hora}"
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
class PetTutor(models.Model):
    pk = models.CompositePrimaryKey('id_coleira', 'id_tutor')
    id_coleira = models.ForeignKey(Pet, on_delete = models.CASCADE, db_column = 'id_coleira')
    id_tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE, db_column = 'id_tutor')

    class Meta:
        db_table = 'pet_tutor'
        managed = False