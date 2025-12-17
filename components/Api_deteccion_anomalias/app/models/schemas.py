from pydantic import BaseModel, Field
from typing import Optional, List

class MeasurementInput(BaseModel):
    sensor_id: str = Field(..., min_length=1, example="sensor-01")
    valor: float
    timestamp: Optional[float] = None 

class MeasurementOutput(BaseModel):
    sensor_id: str
    valor: float
    timestamp: float
    procesado_por: str
    es_anomalia: bool
    
    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    sensor_id: str
    total_records: int
    measurements: List[dict]