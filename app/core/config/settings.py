from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "API Educação Financeira Inteligente"
    mongodb_url: str
    gemini_api_key: str
    selic_api_url: str = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
    
    # Novas configurações
    enable_memory: bool = True
    enable_analytics: bool = True
    enable_investment_calc: bool = True
    max_conversation_history: int = 10
    investment_simulation_years: int = 5

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()