from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.user import UserRequest
from app.api.schemas.investment import InvestmentSimulationRequest, InvestmentSimulationResponse
from app.api.services.classification import ProfileClassifier
from app.api.services.ia_generator import IAGenerator
from app.api.services.memory_manager import MemoryManager
from app.api.services.investment_calculator import InvestmentCalculator
from app.api.services.analytics_engine import AnalyticsEngine
from app.api.services import mongodb_crud
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Dict, Any
import json

router = APIRouter(prefix="", tags=["API"])

@router.post("/gerar-conteudo", status_code=status.HTTP_201_CREATED)
async def generate_financial_content(
    request: UserRequest, 
    classifier: ProfileClassifier = Depends(),
    ia_generator: IAGenerator = Depends(),
    memory_manager: MemoryManager = Depends(),
    investment_calculator: InvestmentCalculator = Depends(),
    analytics_engine: AnalyticsEngine = Depends()
):
    """Endpoint principal com todas as funcionalidades inteligentes"""
    
    # 1. Classificação do perfil com regex melhorado
     # 2. Encontrar ou criar usuário
    user = await mongodb_crud.find_document("usuarios", {"nome": request.nome, "idade": request.idade})
    user_id = None
    if user:
        user_id = str(user["_id"])
        await mongodb_crud.update_document("usuarios", {"_id": ObjectId(user_id)}, {
            "updated_at": datetime.now(timezone.utc),
            "valor_disponivel_investir": request.valor_disponivel_investir,
            "auto_classificacao": request.auto_classificacao,
            "tempo_investimento": request.tempo_investimento
        })
    else:
        user_data = {
            "nome": request.nome,
            "idade": request.idade,
            "renda_mensal": request.renda_mensal,
            "valor_disponivel_investir": request.valor_disponivel_investir,
            "auto_classificacao": request.auto_classificacao,
            "tempo_investimento": request.tempo_investimento,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        user_id = await mongodb_crud.create_document("usuarios", user_data)

    # 1. Classificação do perfil com regex melhorado, usando histórico de conversas
    conversation_history = await memory_manager.get_user_memory(user_id) if user_id else None
    profile_percentages = classifier.classify_profile(
        request.objetivo_financeiro, 
        request.auto_classificacao,
        request.referencia_texto,
        conversation_history.get("conversation_history") if conversation_history else None
    )
    dominant_profile = max(profile_percentages, key=profile_percentages.get)


    # 3. Cálculos de investimento se houver dados
    investment_simulation = None
    if request.valor_disponivel_investir and request.tempo_investimento:
        investment_simulation = await investment_calculator.simulate_investment_scenarios(
            initial=request.valor_disponivel_investir,
            monthly=request.renda_mensal * 0.2,  # 20% da renda como aporte
            years=request.tempo_investimento,
            profile=dominant_profile
        )

    # 4. Análise comparativa
    peer_analysis = await analytics_engine.compare_with_peers(request.model_dump())

    # 5. Geração de conteúdo com contexto de memória
    conversation_context = await memory_manager.get_conversation_context(user_id)
    user_data = request.model_dump()
    user_data["investment_simulation"] = investment_simulation
    user_data["peer_analysis"] = peer_analysis

    generated_content = await ia_generator.generate_content(
        dominant_profile, 
        user_data, 
        request.objetivo_financeiro,
        conversation_context
    )

    # 6. Atualizar memória
    await memory_manager.update_user_memory(user_id, {
        "request": user_data,
        "response": generated_content,
        "profile": dominant_profile,
        "objective": request.objetivo_financeiro,
        "dominant_profile": dominant_profile
    })

    # 7. Salvar histórico
    history_data = {
        "user_id": user_id,
        "request": user_data,
        "response": generated_content,
        "investment_simulation": investment_simulation,
        "peer_analysis": peer_analysis,
        "timestamp": datetime.now(timezone.utc)
    }
    await mongodb_crud.create_document("historico", history_data)

    return {
        "perfil_investidor": dominant_profile,
        "percentuais_perfil": profile_percentages,
        "conteudo_educativo": generated_content,
        "simulacao_investimento": investment_simulation,
        "analise_comparativa": peer_analysis,
        "user_id": user_id
    }

@router.post("/simular-investimento", response_model=InvestmentSimulationResponse)
async def simulate_investment(request: InvestmentSimulationRequest):
    """Endpoint específico para simulação de investimentos"""
    calculator = InvestmentCalculator()
    result = await calculator.calculate_compound_interest(
        request.valor_inicial,
        request.aporte_mensal,
        request.tempo_anos,
        request.taxa_anual
    )
    
    result["projecao_mensal"] = calculator.generate_monthly_projection(
        request.valor_inicial,
        request.aporte_mensal,
        request.tempo_anos,
        request.taxa_anual
    )
    
    return result