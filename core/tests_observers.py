from unittest.mock import MagicMock
from django.test import SimpleTestCase
from core.observers import Observer, Subject


class ObserverPatternUnitTest(SimpleTestCase):
    """
    Testes de unidade para validar o comportamento base do padrão Observer
    implementado no módulo core.observers.
    """

    def test_notifica_todos_os_observers_anexados(self):
        # Arrange (Preparação)
        subject = Subject()
        observer_1 = MagicMock(spec=Observer)
        observer_2 = MagicMock(spec=Observer)

        subject.anexar(observer_1)
        subject.anexar(observer_2)

        dados_evento = {
            "pet_nome": "Rex",
            "distancia_metros": 180.5,
            "raio_permitido": 100.0,
        }

        # Act (Ação)
        subject.notificar("SAIDA_RAIO", dados_evento)

        # Assert (Verificação)
        observer_1.atualizar.assert_called_once_with("SAIDA_RAIO", dados_evento)
        observer_2.atualizar.assert_called_once_with("SAIDA_RAIO", dados_evento)

    def test_nao_notifica_observer_desanexado_e_evita_duplicidade(self):
        # Arrange
        subject = Subject()
        observer_ativo = MagicMock(spec=Observer)
        observer_removido = MagicMock(spec=Observer)

        # Tenta anexar o mesmo observer duas vezes para garantir idempotência
        subject.anexar(observer_ativo)
        subject.anexar(observer_ativo)
        subject.anexar(observer_removido)

        # Remove o segundo observer antes do disparo
        subject.desanexar(observer_removido)

        dados_evento = {"pet_nome": "Luna", "status": "FORA_DO_RAIO"}

        # Act
        subject.notificar("SAIDA_RAIO", dados_evento)

        # Assert
        observer_ativo.atualizar.assert_called_once_with("SAIDA_RAIO", dados_evento)
        observer_removido.atualizar.assert_not_called()