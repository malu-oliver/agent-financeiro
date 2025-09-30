from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações da API
    app_name: str = "API Educação Financeira"
    app_version: str = "1.0.0"
    app_description: str = "Sistema inteligente de educação financeira com IA"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"
    
    # Banco de Dados MongoDB
    mongodb_url: str = ""
    mongo_connection_string: str = ""
    database_name: str = "educacao_financeira"
    
    # API Gemini
    gemini_api_key: str = ""
    
    # Configurações adicionais
    default_currency: str = "BRL"
    secret_key: str = "your-secret-key-here"
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000,http://localhost:8501"
    cache_ttl: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def mongodb_connection_url(self) -> str:
        """Retorna a URL de conexão do MongoDB"""
        return self.mongodb_url or self.mongo_connection_string

    @property
    def mongo_db_name(self) -> str:
        """Retorna o nome do database"""
        return self.database_name

settings = Settings()