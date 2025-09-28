from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.connection import connect_to_mongo, close_mongo_connection, mongodb
#from app.api.routes.content import router as content_router
from app.api.routes.content import router as content_router  # ← CORRIGIDO
from app.core.config.settings import settings
from app.api.services.ia_generator import IAGenerator
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Evento de startup
    print("Iniciando a aplicação...")
    await connect_to_mongo()
    
    # Validar conexão com a IA
    try:
        ia_gen = IAGenerator()
        if not await ia_gen.check_connection():
            print("Aviso: Conexão com o serviço de IA não estabelecida. Verifique a chave de API.")
    except Exception as e:
        print(f"Aviso sobre IA: {e}")

    yield
    # Evento de shutdown
    print("Encerrando a aplicação...")
    await close_mongo_connection()

app = FastAPI(
    title="ZUP Educação Financeira AI - Sistema Inteligente",
    description="Sistema inteligente de educação financeira com classificação automática de perfil de investidor",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(content_router, prefix="/api", tags=["API"])

@app.get("/", status_code=status.HTTP_200_OK, summary="Página inicial")
async def root():
    """Página inicial da API"""
    return {
        "message": "Bem-vindo à API de Educação Financeira Inteligente",
        "version": "4.0.0",
        "status": "online"
    }

@app.get("/health", status_code=status.HTTP_200_OK, summary="Verifica a saúde da API")
async def health_check():
    """Verifica o status da conexão com o MongoDB e a disponibilidade da IA."""
    try:
        # Verificar MongoDB
        if mongodb.client:
            await mongodb.client.admin.command('ping')
            mongo_status = "connected"
        else:
            mongo_status = "disconnected"
    except Exception:
        mongo_status = "error"

    # Verificar IA (mais tolerante)
    try:
        ia_gen = IAGenerator()
        ia_status = "connected" if await ia_gen.check_connection() else "disconnected"
    except Exception:
        ia_status = "error"

    return {
        "status": "ok" if mongo_status == "connected" else "degraded",
        "mongodb": mongo_status,
        "ia_service": ia_status,
        "version": "4.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)