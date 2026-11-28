from abc import ABC, abstractmethod
from typing import Any, List


class Observer(ABC):
    """
    Interface base (Observador) para qualquer classe que deseje
    reagir a eventos disparados por um Subject no sistema PetFinder.
    """

    @abstractmethod
    def atualizar(self, evento: str, dados: dict[str, Any]) -> None:
        """
        Método invocado automaticamente pelo Subject quando ocorre um evento.
        
        :param evento: Identificador do evento (ex: 'SAIDA_RAIO', 'PERDA_SINAL').
        :param dados: Dicionário com as informações relevantes do contexto do evento.
        """
        pass


class Subject:
    """
    Classe base (Observado/Publicador) responsável por gerenciar a lista
    de observadores interessados e notificá-los quando um evento ocorrer.
    """

    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def anexar(self, observer: Observer) -> None:
        """Inscreve um novo observador se ele ainda não estiver na lista."""
        if observer not in self._observers:
            self._observers.append(observer)

    def desanexar(self, observer: Observer) -> None:
        """Remove um observador da lista de notificações."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notificar(self, evento: str, dados: dict[str, Any]) -> None:
        """Notifica todos os observadores inscritos sobre a ocorrência de um evento."""
        for observer in self._observers:
            observer.atualizar(evento, dados)