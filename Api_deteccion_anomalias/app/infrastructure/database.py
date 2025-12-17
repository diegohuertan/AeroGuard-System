import redis
from redis.sentinel import Sentinel
import time
import logging
from app.core.config import settings

logger = logging.getLogger("infrastructure")
logging.basicConfig(level=logging.INFO)

class RedisManager:
    def __init__(self):
        self.sentinel_connection = None
        self.master_connection = None

    def connect(self):
        retries = 5
        delay = 2
        while retries > 0:
            try:
                logger.info(f"Conectando a Sentinel en {settings.REDIS_SENTINEL_HOST}:{settings.REDIS_SENTINEL_PORT}...")
                self.sentinel_connection = Sentinel(
                    [(settings.REDIS_SENTINEL_HOST, settings.REDIS_SENTINEL_PORT)],
                    socket_timeout=0.5
                )
                self.master_connection = self.sentinel_connection.master_for(
                    settings.REDIS_MASTER_SET,
                    socket_timeout=0.5,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                if self.master_connection.ping():
                    logger.info("✅ Conectado a Redis Master")
                    return
            except Exception as e:
                logger.warning(f"⚠️ Redis no listo ({e}). Reintentando en {delay}s...")
                time.sleep(delay)
                retries -= 1
                delay *= 2
        logger.error("❌ Fallo crítico: Redis no disponible.")

    def get_client(self):
        if not self.master_connection:
            self.connect()
        return self.master_connection

redis_manager = RedisManager()