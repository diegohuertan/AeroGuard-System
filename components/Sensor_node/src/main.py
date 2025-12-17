import os
import sys
import logging
import signal

from application.sensor_service import SensorService
from infrastructure.zookeeper_adapter import ZooKeeperAdapter
from infrastructure.http_api_adapter import HttpApiAdapter

# Configuración del logging para que sea informativo, incluyendo el nombre del hilo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    """
    Punto de entrada de la aplicación (Entrypoint).
    1. Lee la configuración desde argumentos y variables de entorno.
    2. Realiza la Inyección de Dependencias (instancia adaptadores y servicio).
    3. Inicia el servicio.
    4. Gestiona una parada ordenada (graceful shutdown).
    """
    # 1. Leer configuración
    try:
        sensor_id = sys.argv[1]
    except IndexError:
        logging.error("Error: Se requiere el ID del sensor como primer argumento de línea de comandos.")
        sys.exit("Uso: python main.py <sensor-id>")

    zoo_hosts = os.getenv("ZOO_HOSTS")
    if not zoo_hosts:
        logging.error("Error: La variable de entorno ZOO_HOSTS no está definida.")
        sys.exit("Error: ZOO_HOSTS no definida.")

    api_url = os.getenv("API_URL")
    if not api_url:
        logging.error("Error: La variable de entorno API_URL no está definida.")
        sys.exit("Error: API_URL no definida.")
    
    logging.info("--- Configuración del Nodo Sensor ---")
    logging.info(f"ID del Sensor:    {sensor_id}")
    logging.info(f"ZooKeeper Hosts:  {zoo_hosts}")
    logging.info(f"URL de la API:      {api_url}")
    logging.info("------------------------------------")

    service: SensorService = None

    def graceful_shutdown(signum, frame):
        logging.warning(f"Señal de parada recibida (Signal {signum}). Iniciando apagado ordenado...")
        if service:
            service.stop()

    # Registrar manejadores para las señales de terminación
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    try:
        # 2. Inyección de Dependencias
        logging.info("Inicializando adaptadores y servicio...")
        zk_adapter = ZooKeeperAdapter(hosts=zoo_hosts, sensor_id=sensor_id)
        http_adapter = HttpApiAdapter(api_url=api_url)
        
        service = SensorService(
            sensor_id=sensor_id,
            zk_adapter=zk_adapter,
            http_adapter=http_adapter
        )

        # 3. Arrancar el servicio
        service.run()

    except Exception as e:
        logging.critical(f"Error fatal durante la inicialización o ejecución: {e}", exc_info=True)
    finally:
        logging.info("El programa principal ha finalizado.")

if __name__ == "__main__":
    main()
