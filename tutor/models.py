from django.db import models


class Usuario(models.Model):
    # Tabela `usuario` do Banco_dados.sql
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length = 100)
    #Verificação do email e mensagem de erro caso exista duplicatas do mesmo;
    email = models.EmailField(
        max_length = 120,
        unique = True,
        error_messages = {'unique': "Erro: Este e-mail ja está sendo usado!"},
    )
    telefone = models.CharField(max_length = 11)
    senha_hash = models.CharField(max_length = 255)

    class Meta:
        db_table = 'usuario'
        managed = False
        
    def __str__(self):
        return self.nome


class Tutor(models.Model):
    # Tabela `tutor`: eh um `usuario` (1:1) que possui pets
    id_tutor = models.OneToOneField(
        Usuario,
        on_delete = models.CASCADE,
        primary_key = True,
        db_column = 'id_tutor',
    )

    class Meta:
        db_table = 'tutor'
        managed = False

    def __str__(self):
        return self.id_tutor.nome


class ContatoEmergencia(models.Model):
    # Tabela `contato_emergencia`: outro `usuario` ligado a um `tutor`
    class Parentesco(models.TextChoices):
        PAI = 'Pai', 'Pai'
        MAE = 'Mãe', 'Mãe'
        FILHO_A = 'Filho(a)', 'Filho(a)'
        AMIGO_A = 'Amigo(a)', 'Amigo(a)'
        CONJUGE = 'Cônjuge', 'Cônjuge'
        OUTROS = 'Outros', 'Outros'

    pk = models.CompositePrimaryKey('id_contato', 'id_tutor')
    id_contato = models.ForeignKey(Usuario, on_delete = models.CASCADE, db_column = 'id_contato')
    id_tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE, db_column = 'id_tutor')
    parentesco = models.CharField(max_length = 20, choices = Parentesco.choices)

    class Meta:
        db_table = 'contato_emergencia'
        managed = False

class Endereco(models.Model):
    # Tabela `endereco`
    id_endereco = models.AutoField(primary_key=True)
    id_tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE, db_column = 'id_tutor')
    cep = models.CharField(max_length = 8)
    logradouro = models.CharField(max_length = 150)
    bairro = models.CharField(max_length = 80, blank = True, null = True)
    numero = models.CharField(max_length = 10, blank = True, null = True)
    cidade = models.CharField(max_length = 80)
    estado = models.CharField(max_length = 2)
    latitude = models.DecimalField(max_digits = 9, decimal_places = 6, blank = True, null = True)
    longitude = models.DecimalField(max_digits = 9, decimal_places = 6, blank = True, null = True)

    class Meta:
        db_table = 'endereco'
        managed = False

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.cidade}/{self.estado}"