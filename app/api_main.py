"""
ZUP Educação Financeira AI - Configuração Principal da API

Este módulo configura a aplicação FastAPI principal, incluindo:
- Configuração de CORS para permitir requests de diferentes origens
- Inclusão das rotas da API com prefixo /api/v1
- Endpoints informativos (root, health check, perfis de investidor)
- Documentação automática via Swagger UI e ReDoc

Autor: Equipe ZUP AI Camp para Minas
Data: 18 de setembro de 2025
Versão: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.api_routes import router as api_router
from app.api.services.database import connect_to_mongo, close_mongo_connection, ping_database
from app.api.services.ia_generator import IAGenerator

# Configuração principal da aplicação FastAPI
app = FastAPI(
    title="ZUP Educação Financeira AI",
    description="Sistema inteligente de educação financeira com classificação automática de perfil de investidor",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Eventos de lifecycle

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    print("🚀 API iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    print("🛑 API encerrada com sucesso!")

# Definir as origens permitidas para CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",  # Para futuro frontend React/Vue
    "http://127.0.0.1:3000",
    "http://localhost:8501",  # Streamlit
    "http://127.0.0.1:8501",
]

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir as rotas da API
app.include_router(api_router, prefix="/api/v1", tags=["API"])

@app.get("/", tags=["Info"])
async def root():
    """
    Endpoint raiz da API que retorna informações gerais sobre o sistema.
    """
    return {
        "message": "ZUP Educação Financeira AI - API funcionando!",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "health": "/health",
            "perfis": "/perfis-investidor",
            "gerar_conteudo": "/api/v1/gerar-conteudo",
            "crud": {
                "usuarios": "/api/v1/usuarios",
                "historico": "/api/v1/historico",
                "estatisticas": "/api/v1/estatisticas"
            }
        }
    }

@app.get("/health", tags=["Info"])
async def health_check():
    """Health check dinâmico verificando API, MongoDB e Serviço de IA."""
    mongo_ok = await ping_database()
    ia_gen = IAGenerator()
    ia_ok = await ia_gen.check_connection()

    status = "healthy" if mongo_ok else "degraded"
    if not mongo_ok and not ia_ok:
        status = "unhealthy"

    return {
        "service": "ZUP Educação Financeira AI",
        "status": status,
        "database": "MongoDB Atlas - Conectado" if mongo_ok else "MongoDB - Indisponível (modo simulação)",
        "ai_service": "Google Gemini - Ativo" if ia_ok else "IA - Chave ausente ou inválida",
        "documentation": {"swagger": "/docs", "redoc": "/redoc"}
    }

@app.get("/perfis-investidor", tags=["Info"])
async def get_perfis_investidor():
    """
    Endpoint informativo sobre os perfis de investidor disponíveis no sistema.
    """
    return {
        "perfis_disponveis": ["conservador", "moderado", "agressivo"],
        "descricoes": {
            "conservador": "Baixo risco, foco em preservação de capital",
            "moderado": "Risco equilibrado, crescimento com segurança",
            "agressivo": "Alto risco, potencial de retorno elevado"
        },
        "exemplo_uso": "POST /api/v1/gerar-conteudo com dados do usuário"
    }