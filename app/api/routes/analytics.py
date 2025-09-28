from fastapi import APIRouter, HTTPException
from app.api.services.memory_manager import MemoryManager
from app.api.services.investment_calculator import InvestmentCalculator
from app.api.schemas.investment import InvestmentSimulation, InvestmentResponse

router = APIRouter()
memory_manager = MemoryManager()
calculator = InvestmentCalculator()

@router.post("/simular-investimento", response_model=InvestmentResponse)
async def simular_investimento(simulacao: InvestmentSimulation):
    """Simula investimento com juros compostos"""
    try:
        resultado = calculator.simular_investimento(simulacao)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na simulação: {str(e)}")

@router.get("/analise-comparativa/{user_id}")
async def analise_comparativa(user_id: str):
    """Fornece análise comparativa com usuários similares"""
    # Buscar dados do usuário
    usuario = await memory_manager.find_document("usuarios", {"_id": user_id})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Encontrar usuários similares
    similares = await memory_manager.get_similar_users(
        (usuario['idade']-5, usuario['idade']+5),
        (usuario['renda_mensal']*0.7, usuario['renda_mensal']*1.3),
        usuario.get('objetivo_financeiro', '')
    )
    
    return {
        "usuario": usuario,
        "total_similares": len(similares),
        "perfil_medio": self.calcular_perfil_medio(similares),
        "recomendacoes_baseadas_similares": self.gerar_recomendacoes_similares(similares)
    }