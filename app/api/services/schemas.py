from pydantic import BaseModel, Field
from typing import Optional, List

class UserRequest(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário")
    idade: int = Field(..., ge=18, le=100, description="Idade do usuário")
    renda: float = Field(..., ge=0, description="Renda mensal em R$")
    objetivo_financeiro: str = Field(..., description="Objetivo financeiro principal")
    email: Optional[str] = Field(None, description="E-mail para identificação única")  # REMOVIDO EmailStr
    valor_investir: Optional[float] = Field(0, ge=0, description="Valor disponível para investir")
    auto_classificacao: Optional[str] = Field(None, description="Como o usuário se classifica")
    referencias: Optional[str] = Field(None, description="Referências ou contexto adicional")

class InvestmentSimulation(BaseModel):
    valor_inicial: float = Field(..., ge=0, description="Valor inicial do investimento")
    aporte_mensal: float = Field(..., ge=0, description="Aporte mensal")
    tempo_anos: int = Field(..., ge=1, le=50, description="Tempo em anos")
    taxa_anual: Optional[float] = Field(None, description="Taxa de juros anual (%)")
    perfil_risco: str = Field(..., description="Perfil de risco")