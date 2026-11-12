from django.db import models
from tutor.models import Tutor, Usuario 

class Clinica(models.Model):
    # Tabela `clinica`
    id_clinica = models.AutoField(primary_key=True)
    nome = models.CharField(max_length = 100)
    endereco = models.CharField(max_length = 200)
    telefone = models.CharField(max_length = 20, blank = True, null = True)

    class Meta:
        db_table = 'clinica'
        managed = False

    def __str__(self):
        return self.nome

class HorarioFuncionamento(models.Model):
    # Tabela `horario_funcionamento`
    pk = models.CompositePrimaryKey('id_clinica', 'dia_semana')
    id_clinica = models.ForeignKey(Clinica, on_delete = models.CASCADE, db_column = 'id_clinica')
    dia_semana = models.PositiveSmallIntegerField()
    abre = models.TimeField()
    fecha = models.TimeField()

    class Meta:
        db_table = 'horario_funcionamento'
        managed = False
        constraints = [
            models.CheckConstraint(
                condition = models.Q(dia_semana__gte = 1, dia_semana__lte = 7),
                name = 'ck_horario_dia_semana',
            ),
        ]

    def __str__(self):
        return f"{self.id_clinica} - dia {self.dia_semana}"

class TutorClinica(models.Model):
    # Tabela `tutor_clinica`: clinicas favoritas do tutor
    pk = models.CompositePrimaryKey('id_tutor', 'id_clinica')
    id_tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE, db_column = 'id_tutor')
    id_clinica = models.ForeignKey(Clinica, on_delete = models.CASCADE, db_column = 'id_clinica')

    class Meta:
        db_table = 'tutor_clinica'
        managed = False