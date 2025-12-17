from dataclasses import dataclass
from datetime import datetime

@dataclass
class Medicion:
    """
    Representa una única medición de un sensor.
    Es un objeto de valor simple sin comportamiento, parte del núcleo del dominio.
    """
    sensor_id: str
    valor: float
    timestamp: datetime
