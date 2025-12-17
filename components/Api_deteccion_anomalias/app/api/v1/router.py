from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.database import redis_manager
from app.repositories.measurement_repo import MeasurementRepository
from app.services.anomaly_service import AnomalyService
from app.models.schemas import MeasurementInput, MeasurementOutput, HistoryResponse

router = APIRouter()

def get_service():
    client = redis_manager.get_client()
    if not client:
        raise HTTPException(status_code=503, detail="Redis no disponible")
    repo = MeasurementRepository(client)
    return AnomalyService(repo)

@router.post("/nuevo", response_model=MeasurementOutput)
def registrar(data: MeasurementInput, service: AnomalyService = Depends(get_service)):
    return service.process_measurement(data.sensor_id, data.valor)

@router.get("/listar", response_model=HistoryResponse)
def listar(sensor_id: str, service: AnomalyService = Depends(get_service)):
    return service.get_history(sensor_id)

@router.get("/detectar")
def detectar_anomalia(
    sensor_id: str, 
    valor: float, 
    service: AnomalyService = Depends(get_service)
):
    return service.evaluate_measurement(sensor_id, valor)