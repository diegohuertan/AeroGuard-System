from fastapi import FastAPI, HTTPException
from app.infrastructure.database import redis_manager
from app.api.v1.router import router
from app.core.config import settings
# Eliminamos 'import uvicorn' porque solo lo usa el bloque __main__

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

@app.on_event("startup")
async def startup():
    # Tu conexión resiliente
    try:
        redis_manager.connect()
    except:
        pass

app.include_router(router, prefix=settings.API_V1_STR)

# --- ENDPOINT DE VERIFICACIÓN CRÍTICA (HEALTHCHECK) ---
# Si Redis falla, este endpoint devuelve 503, y Docker Swarm marca el servicio como no sano
@app.get("/health")
def health_check():
    # Verificamos que la conexión persistente esté activa
    is_master_connected = bool(redis_manager.master_connection)
    if is_master_connected:
        return {"status": "ok", "redis": "conectado"}
        
    # Devolver 503 hace que el healthcheck de Docker falle y reinicie el contenedor
    raise HTTPException(status_code=503, detail="Redis connection failed during health check")

# NO DEBE HABER NADA MÁS DEBAJO. NO if __name__ == "__main__":