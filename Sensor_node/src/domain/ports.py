from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Medicion

class IZooKeeperAdapter(ABC):
    """
    Interfaz que define el contrato para el adaptador de ZooKeeper.
    Abstrae los detalles de la comunicación y coordinación con el clúster de ZooKeeper.
    Esta es una interfaz del lado de la "infraestructura" que la aplicación usará.
    """

    @abstractmethod
    def run_for_leader(self, on_become_leader_callback: Callable[[], None]) -> None:
        """
        Inicia la participación en la elección de líder.

        Args:
            on_become_leader_callback: Una función que se ejecutará en un hilo
                                       cuando este nodo se convierta en líder.
                                       La implementación de esta función debe contener
                                       el bucle principal del líder.
        """
        pass

    @abstractmethod
    def am_i_leader(self) -> bool:
        """Verifica si el nodo actual ostenta el liderazgo."""
        pass

    @abstractmethod
    def trigger_measurement_round(self) -> None:
        """
        (Solo Líder) Publica un evento para que los seguidores inicien una medición.
        """
        pass

    @abstractmethod
    def watch_measurement_round(self, on_trigger_callback: Callable[[], None]) -> None:
        """
        (Solo Seguidores) Observa el evento de inicio de ronda y ejecuta un callback.
        """
        pass

    @abstractmethod
    def publish_measurement(self, valor: float) -> None:
        """
        Publica la medición del sensor en un nodo efímero en ZooKeeper.
        """
        pass

    @abstractmethod
    def get_all_measurements(self) -> List[Medicion]:
        """
        (Solo Líder) Obtiene todas las mediciones publicadas por los seguidores.
        """
        pass
    
    @abstractmethod
    def clear_measurements(self) -> None:
        """
        (Solo Líder) Elimina las mediciones de la ronda actual.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Detiene el adaptador y cierra la conexión con ZooKeeper de forma segura.
        """
        pass


class IHttpApiAdapter(ABC):
    """
    Interfaz para el adaptador que se comunica con la API HTTP externa.
    """

    @abstractmethod
    def send_average(self, average: float) -> bool:
        """
        Envía el valor promedio calculado a la API.

        Args:
            average: El valor promedio de las mediciones.

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        pass
