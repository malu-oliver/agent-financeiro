import httpx
from typing import Optional, Dict, Any
from datetime import datetime
import json

class SelicAPI:
    def __init__(self):
        self.base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
        
    async def get_current_selic(self) -> Optional[float]:
        """Obtém a taxa Selic atual"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/ultimos/1", timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    return float(data[0]['valor'])
                return None
                
        except Exception as e:
            print(f"Erro ao obter taxa Selic: {e}")
            return None
    
    async def get_selic_history(self, days: int = 30) -> Optional[list]:
        """Obtém histórico da Selic"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/ultimos/{days}", timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                if data and isinstance(data, list):
                    return data
                return None
                
        except Exception as e:
            print(f"Erro ao obter histórico Selic: {e}")
            return None

# Fallback para quando a API não estiver disponível
class MockSelicAPI:
    def __init__(self):
        self.mock_selic = 0.1175  # 11.75% ao ano
        
    async def get_current_selic(self) -> float:
        return self.mock_selic
    
    async def get_selic_history(self, days: int = 30) -> list:
        return [{"data": "2024-01-01", "valor": self.mock_selic}]