from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class InvestmentSimulationRequest(BaseModel):
    valor_inicial: float
    aporte_mensal: float
    tempo_anos: int
    taxa_anual: float
    perfil_risco: str

class InvestmentSimulationResponse(BaseModel):
    valor_final: float
    total_investido: float
    juros_acumulados: float
    projecao_mensal: List[Dict[str, float]]
    metricas: Dict[str, float]

class SelicData(BaseModel):
    data: datetime
    valor: float

