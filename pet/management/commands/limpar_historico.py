from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from pet.models import HistoricoLocalizacao


class Command(BaseCommand):
    help = "Remove registros de localização com mais de 30 dias."

    def handle(self, *args, **kwargs):
        data_limite = timezone.now() - timedelta(days=30)
        deletados, _ = HistoricoLocalizacao.objects.filter(
            data_hora__lt=data_limite
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(f"{deletados} registros antigos removidos com sucesso.")
        )