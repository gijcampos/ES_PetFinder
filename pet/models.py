from django.db import models
from usuarios.models import Tutor, Usuario


class Pet(models.Model):
    # Tabela `pet`: o id da coleira e a chave primaria
    id_coleira = models.CharField(max_length = 9, primary_key = True)
    # Sem ON DELETE no SQL, logo o padrao e RESTRICT
    id_tutor = models.ForeignKey(Tutor, on_delete = models.RESTRICT, db_column = 'id_tutor')
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


class Notificacao(models.Model):
    # Tabela `notificacao`
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