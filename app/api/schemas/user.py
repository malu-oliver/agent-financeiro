from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserSelfAssessment(str, Enum):
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    AGRESSIVO = "agressivo"
    INDEFINIDO = "indefinido"

class UserRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=50, description="Nome do usuário")
    idade: int = Field(..., gt=0, lt=120, description="Idade do usuário")
    renda_mensal: float = Field(..., gt=0, description="Renda mensal do usuário")
    objetivo_financeiro: str = Field(..., min_length=10, max_length=1500, description="Objetivo financeiro do usuário")
    
    # Novos campos
    valor_disponivel_investir: Optional[float] = Field(None, gt=0, description="Valor disponível para investir")
    auto_classificacao: Optional[UserSelfAssessment] = Field(None, description="Como o usuário se classifica")
    referencia_texto: Optional[str] = Field(None, max_length=2000, description="Texto de referência para análise")
    tempo_investimento: Optional[int] = Field(None, gt=0, le=50, description="Tempo em anos para investimento")
    dominant_profile: Optional[UserSelfAssessment] = Field(None, description="Perfil dominante do usuário, se já classificado")

    @validator('valor_disponivel_investir')
    def validate_investment_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "idade": 30,
                "renda_mensal": 5000.00,
                "objetivo_financeiro": "Quero guardar dinheiro para comprar um apartamento em 5 anos",
                "valor_disponivel_investir": 10000.00,
                "auto_classificacao": "moderado",
                "tempo_investimento": 5
            }
        }

class UserResponse(BaseModel):
    id: str
    nome: str
    idade: int
    renda_mensal: float
    created_at: datetime
    updated_at: Optional[datetime]

class UserMemory(BaseModel):
    user_id: str
    conversation_history: List[Dict[str, Any]]
    last_interaction: datetime
    preferences: Dict[str, Any]
    dominant_profile: Optional[UserSelfAssessment]