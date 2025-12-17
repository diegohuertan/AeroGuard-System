import logging
import requests
from requests.exceptions import RequestException

from ..domain.ports import IHttpApiAdapter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HttpApiAdapter(IHttpApiAdapter):
    """
    Implementación del adaptador HTTP para comunicarse con la API externa (Legacy).
    Utiliza la librería `requests` para realizar llamadas POST.
    """

    def __init__(self, api_url: str):
        if not api_url or not api_url.startswith("http"):
            raise ValueError("La URL de la API es inválida.")
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "SensorNodeClient/1.0"
        })

    def send_average(self, average: float) -> bool:
        """
        Envía el valor promedio de las mediciones a la API configurada.

        Args:
            average: El valor flotante de la media calculada.

        Returns:
            True si la API devuelve un código 2xx, False en cualquier otro caso.
        """
        # El payload esperado por la API de la Práctica 2
        payload = {"valor_medio": average}
        logging.info(f"Enviando media {average:.2f} a la API en {self.api_url}")

        try:
            # Es CRÍTICO definir un timeout para evitar bloqueos indefinidos.
            response = self.session.post(self.api_url, json=payload, timeout=5.0)
            
            # Lanza una excepción HTTPError para respuestas 4xx/5xx.
            response.raise_for_status()
            
            logging.info(f"Media enviada correctamente. Respuesta de la API: {response.status_code}")
            return True
        except RequestException as e:
            # Captura errores de conexión, timeouts, DNS, etc.
            logging.error(f"Error de red al contactar la API: {e}")
            return False
        except Exception as e:
            # Captura cualquier otro error inesperado.
            logging.error(f"Error inesperado al enviar datos a la API: {e}")
            return False
