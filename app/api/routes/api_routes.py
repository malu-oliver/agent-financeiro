from fastapi import APIRouter, Depends, HTTPException, status
from app.api.services.schemas import UserRequest, InvestmentSimulation
from app.api.services.ia_classification import ProfileClassifier
from app.api.services.ia_generator import IAGenerator
from app.api.services.financial_calculator import FinancialCalculator
from app.api.services import database
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Dict, Any
import hashlib

router = APIRouter()

# ==================== FUNÇÕES AUXILIARES ====================

def generate_user_hash(email: str, nome: str) -> str:
    """Gera hash único para usuário baseado em email e nome"""
    if email:
        unique_string = f"{email.lower()}_{nome.lower()}"
    else:
        unique_string = f"anonymous_{nome.lower()}_{datetime.now().timestamp()}"
    return hashlib.sha256(unique_string.encode()).hexdigest()

def serialize_doc(doc):
    """Converte ObjectId do MongoDB para string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# ==================== ENDPOINT PRINCIPAL IA ====================

@router.post("/gerar-conteudo", status_code=status.HTTP_201_CREATED, summary="Gera conteúdo de educação financeira personalizado com IA Agente")
async def generate_financial_content(request: UserRequest, classifier: ProfileClassifier = Depends(), ia_generator: IAGenerator = Depends()):
    """Recebe os dados do usuário, classifica o perfil e gera conteúdo personalizado usando características de Agente de IA."""

    # GERAR ID ÚNICO DO USUÁRIO
    user_hash = generate_user_hash(request.email, request.nome)
    
    # Busca ou cria usuário para manter contexto
    user = await database.find_document("usuarios", {"user_hash": user_hash})
    if user:
        user_id = str(user["_id"])
        # Atualiza dados se necessário
        await database.update_document("usuarios", {"_id": user["_id"]}, {
            "nome": request.nome,
            "idade": request.idade,
            "renda": request.renda,
            "email": request.email,
            "valor_investir": request.valor_investir,
            "auto_classificacao": request.auto_classificacao,
            "updated_at": datetime.now(timezone.utc)
        })
    else:
        user_id = await database.create_document("usuarios", {
            "user_hash": user_hash,
            "nome": request.nome,
            "idade": request.idade,
            "renda": request.renda,
            "email": request.email,
            "valor_investir": request.valor_investir,
            "auto_classificacao": request.auto_classificacao,
            "referencias": request.referencias,
            "created_at": datetime.now(timezone.utc)
        })

    # 1. Classificar o perfil com aprendizado contínuo
    profile_percentages = classifier.classify_profile(
        request.objetivo_financeiro, user_id)
    
    # CORREÇÃO: Remover campos internos antes de encontrar o perfil dominante
    profile_data = {k: v for k, v in profile_percentages.items() if not k.startswith('_')}
    dominant_profile = max(profile_data, key=profile_data.get)

    # PERCEPÇÃO AMBIENTAL: Analisa evolução do usuário
    user_evolution = classifier.analyze_user_evolution(user_id)

    # 2. Gerar conteúdo com comportamento autônomo
    user_data = request.model_dump()
    generated_content = await ia_generator.generate_content(dominant_profile, user_data, request.objetivo_financeiro, user_id)

    if "Erro" in generated_content or "Não foi possível" in generated_content:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=generated_content)

    # AUTONOMIA: Obter sugestões autônomas do agente
    autonomous_suggestions = await ia_generator.get_autonomous_suggestions(user_id)

    # 3. Salvar dados com contexto expandido
    profile_data = {
        "user_id": user_id,
        "user_hash": user_hash,
        "perfil_classificado": dominant_profile,
        "percentuais": profile_percentages,
        "objetivo": request.objetivo_financeiro,
        "user_evolution": user_evolution,
        "autonomous_suggestions": autonomous_suggestions,
        "timestamp": datetime.now(timezone.utc)
    }
    await database.create_document("perfis", profile_data)

    history_data = {
        "user_id": user_id,
        "user_hash": user_hash,
        "request": user_data,
        "response": generated_content,
        "autonomous_behavior": autonomous_suggestions,
        "user_evolution": user_evolution,
        "timestamp": datetime.now(timezone.utc)
    }
    await database.create_document("historico", history_data)

    # RESPOSTA EXPANDIDA COM CARACTERÍSTICAS DE AGENTE IA
    return {
        "perfil_investidor": dominant_profile,
        "percentuais_perfil": profile_percentages,
        "conteudo_educativo": generated_content,
        "agente_ia": {
            "comportamento_autonomo": autonomous_suggestions["autonomous_action"],
            "sugestoes_inteligentes": autonomous_suggestions["suggestions"],
            "nivel_aprendizado": autonomous_suggestions["learning_progress"],
            "evolucao_usuario": user_evolution,
            "proximas_acoes": autonomous_suggestions.get("suggestions", [])[:3]
        },
        "metadata": {
            "user_id": user_id,
            "user_hash": user_hash,
            "interacoes_anteriores": autonomous_suggestions["interaction_count"],
            "consistencia_perfil": user_evolution["consistency"],
            "tendencia": user_evolution["trend"]
        }
    }

# ==================== NOVOS ENDPOINTS ====================

@router.post("/simular-investimento", summary="Simula investimento com juros compostos")
async def simulate_investment(simulation: InvestmentSimulation):
    """Simula investimento com juros compostos usando taxa Selic ou personalizada"""
    calculator = FinancialCalculator()
    result = await calculator.simulate_investment(simulation.dict())
    
    # Salvar simulação no histórico
    await database.create_document("simulacoes", {
        **simulation.dict(),
        "resultado": result,
        "timestamp": datetime.now(timezone.utc)
    })
    
    return result

@router.get("/usuario/{user_hash}/historico", summary="Obter histórico completo do usuário")
async def get_user_history(user_hash: str):
    """Retorna todo o histórico e evolução do usuário"""
    # Buscar usuário pelo hash
    user = await database.find_document("usuarios", {"user_hash": user_hash})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_id = str(user["_id"])
    
    # Buscar histórico de interações
    historico = await database.find_all_documents("historico", {"user_hash": user_hash})
    
    # Buscar evolução do perfil
    classifier = ProfileClassifier()
    evolucao = classifier.analyze_user_evolution(user_id)
    
    # Buscar simulações anteriores
    simulacoes = await database.find_all_documents("simulacoes", {"user_hash": user_hash})
    
    return {
        "user_info": {
            "nome": user["nome"],
            "email": user.get("email"),
            "data_cadastro": user.get("created_at")
        },
        "evolucao": evolucao,
        "interacoes": [
            {
                "data": interacao.get("timestamp", ""),
                "objetivo": interacao.get("request", {}).get("objetivo_financeiro", "N/A"),
                "perfil": interacao.get("perfil_classificado", "N/A")
            }
            for interacao in historico[:10]
        ],
        "total_interacoes": len(historico),
        "total_simulacoes": len(simulacoes)
    }

@router.get("/benchmark-perfis", summary="Comparativo com outros usuários")
async def get_profile_benchmark():
    """Retorna dados comparativos com base em todos os usuários"""
    todos_usuarios = await database.find_all_documents("usuarios")
    todos_perfis = await database.find_all_documents("perfis")
    
    # Estatísticas básicas
    total_usuarios = len(todos_usuarios)
    if total_usuarios == 0:
        return {"message": "Dados insuficientes para comparação"}
    
    # Distribuição de perfis
    distribuicao = {}
    for perfil in todos_perfis:
        p = perfil.get("perfil_classificado")
        if p:
            distribuicao[p] = distribuicao.get(p, 0) + 1
    
    # Médias
    idades = [u.get("idade", 0) for u in todos_usuarios if u.get("idade")]
    rendas = [u.get("renda", 0) for u in todos_usuarios if u.get("renda")]
    
    return {
        "estatisticas_gerais": {
            "total_usuarios": total_usuarios,
            "idade_media": sum(idades) / len(idades) if idades else 0,
            "renda_media": sum(rendas) / len(rendas) if rendas else 0
        },
        "distribuicao_perfis": {
            perfil: (count / total_usuarios) * 100 
            for perfil, count in distribuicao.items()
        },
        "perfil_mais_comum": max(distribuicao, key=distribuicao.get) if distribuicao else "N/A"
    }

# ==================== ENDPOINTS CRUD (MANTIDOS) ====================

@router.get("/usuarios/{id}", summary="Consulta dados de um usuário específico", response_model=Dict[str, Any])
async def consultar_usuario(id: str):
    """Consulta dados de um usuário específico pelo ID"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    usuario = await database.find_document("usuarios", {"_id": ObjectId(id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return serialize_doc(usuario)

@router.put("/usuarios/{id}", summary="Atualiza dados do usuário", response_model=Dict[str, Any])
async def atualizar_usuario(id: str, perfil: UserRequest):
    """Atualiza dados do usuário existente"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    dados_atualizacao = {
        **perfil.model_dump(),
        "updated_at": datetime.now(timezone.utc)
    }

    modified_count = await database.update_document("usuarios", {"_id": ObjectId(id)}, dados_atualizacao)

    if modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario_atualizado = await database.find_document("usuarios", {"_id": ObjectId(id)})
    return serialize_doc(usuario_atualizado)

@router.delete("/usuarios/{id}", summary="Remove usuário e histórico associado")
async def remover_usuario(id: str):
    """Remove um usuário e todo seu histórico associado"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    deleted_count = await database.delete_document("usuarios", {"_id": ObjectId(id)})
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    await database.delete_document("historico", {"user_id": id})

    return {"message": "Usuário removido com sucesso", "details": "Usuário e histórico associado foram removidos permanentemente"}

@router.get("/usuarios", summary="Listar todos os usuários", response_model=List[Dict[str, Any]])
async def listar_todos_usuarios(limit: int = 10, skip: int = 0):
    """Lista todos os usuários cadastrados (endpoint para desenvolvimento)"""
    usuarios = await database.find_all_documents("usuarios", query={})
    return [serialize_doc(user) for user in usuarios]

@router.post("/usuarios", summary="Criar novo usuário", response_model=Dict[str, Any])
async def criar_usuario(perfil: UserRequest):
    """Cria um novo usuário no sistema"""
    user_hash = generate_user_hash(perfil.email, perfil.nome)
    
    usuario_data = {
        **perfil.model_dump(),
        "user_hash": user_hash,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    user_id = await database.create_document("usuarios", usuario_data)
    usuario_criado = await database.find_document("usuarios", {"_id": ObjectId(user_id)})

    return serialize_doc(usuario_criado)

# ==================== ENDPOINTS DO AGENTE IA ====================

@router.get("/agente-ia/{user_id}/sugestoes", summary="Obter sugestões autônomas do Agente IA")
async def get_autonomous_suggestions(user_id: str, ia_generator: IAGenerator = Depends()):
    """Endpoint específico para obter sugestões autônomas baseadas no aprendizado do agente."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    suggestions = await ia_generator.get_autonomous_suggestions(user_id)
    return {
        "user_id": user_id,
        "agente_ia": suggestions,
        "timestamp": datetime.now(timezone.utc)
    }

@router.get("/agente-ia/{user_id}/evolucao", summary="Análise de evolução do usuário pelo Agente IA")
async def get_user_evolution(user_id: str, classifier: ProfileClassifier = Depends()):
    """Analisa como o perfil do usuário evoluiu ao longo do tempo."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    evolution = classifier.analyze_user_evolution(user_id)
    return {
        "user_id": user_id,
        "evolucao_perfil": evolution,
        "timestamp": datetime.now(timezone.utc)
    }

@router.post("/agente-ia/{user_id}/feedback", summary="Fornecer feedback para aprendizado do Agente")
async def provide_feedback(user_id: str, feedback: dict, ia_generator: IAGenerator = Depends()):
    """Permite que o usuário forneça feedback para o agente aprender e melhorar."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    # Sistema simples de feedback para aprendizado
    feedback_data = {
        "user_id": user_id,
        "feedback": feedback,
        "timestamp": datetime.now(timezone.utc)
    }

    await database.create_document("feedback_agente", feedback_data)

    return {
        "message": "Feedback registrado com sucesso",
        "agente_resposta": "Obrigado! Utilizarei este feedback para melhorar minhas próximas interações.",
        "aprendizado_ativo": True
    }

@router.get("/agente-ia/status", summary="Status do sistema de Agente IA")
async def agent_status(ia_generator: IAGenerator = Depends(), classifier: ProfileClassifier = Depends()):
    """Retorna informações sobre o status e capacidades do sistema de agente IA."""

    # Estatísticas do sistema
    total_users_tracked = len(ia_generator.user_contexts)
    total_interactions = sum(ia_generator.interaction_count.values())
    avg_interactions_per_user = total_interactions / max(total_users_tracked, 1)

    # Obter estatísticas do classificador
    classifier_stats = classifier.get_system_stats()

    return {
        "agente_ia_ativo": True,
        "capacidades": {
            "autonomia_comportamental": True,
            "aprendizado_continuo": True,
            "percepcao_ambiental": True,
            "capacidade_planejamento": True
        },
        "estatisticas": {
            "usuarios_rastreados": total_users_tracked,
            "interacoes_totais": total_interactions,
            "media_interacoes_usuario": round(avg_interactions_per_user, 2),
            "patterns_aprendidos": classifier_stats["effectiveness"]["patterns_learned"],
            "triggers_autonomos": ia_generator.autonomous_triggers
        },
        "versao_agente": "1.0.0",
        "timestamp": datetime.now(timezone.utc)
    }