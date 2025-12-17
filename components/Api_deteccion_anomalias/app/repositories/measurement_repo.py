from redis import Redis
from redis.exceptions import ResponseError
import logging

logger = logging.getLogger("repository")

class MeasurementRepository:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.RETENTION_MS = 86400000

    def save(self, sensor_id: str, value: float, timestamp: float = None) -> int:
        key = f"sensor:{sensor_id}:ts"
        
        try:
            # Capturamos el timestamp que Redis genera
            ts_ms = self.redis.ts().add(key, "*", value) 
            # Devolvemos el timestamp en segundos (dividir por 1000)
            return ts_ms / 1000 
        except ResponseError as e:
            if "key does not exist" in str(e):
                try:
                    self.redis.ts().create(key, retention_msecs=self.RETENTION_MS)
                    return self.save(sensor_id, value)
                except:
                    pass
            raise e

    def get_all(self, sensor_id: str):
        key = f"sensor:{sensor_id}:ts"
        try:
            return self.redis.ts().range(key, "-", "+")
        except:
            return []