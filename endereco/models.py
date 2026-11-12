from django.db import models
from tutor.models import Usuario, Tutor

class Endereco(models.Model):
    id_endereco = models.AutoField(primary_key=True)
    id_tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, db_column='id_tutor')
    cep = models.CharField(max_length=8)
    logradouro = models.CharField(max_length=150)
    bairro = models.CharField(max_length=80, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    cidade = models.CharField(max_length=80)
    estado = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        db_table = 'endereco'
        managed = False

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.cidade}/{self.estado}"