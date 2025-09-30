import httpx
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class FinancialCalculator:
    def __init__(self):
        self.selic_api_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
        
    async def get_selic_rate(self) -> float:
        """Obtém a taxa Selic atual da API do Banco Central"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                "formato": "json",
                "dataInicial": start_date.strftime("%d/%m/%Y"),
                "dataFinal": end_date.strftime("%d/%m/%Y")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.selic_api_url, params=params, timeout=10)
                data = response.json()
                
            if data and len(data) > 0:
                # Pega a última taxa disponível
                latest_rate = float(data[-1]['valor'])
                return latest_rate
            else:
                return 10.25  # Fallback para taxa recente
            
        except Exception as e:
            print(f"Erro ao buscar Selic: {e}")
            return 10.25  # Fallback
    
    def calculate_compound_interest(self, initial: float, monthly: float, years: int, rate: float) -> Dict:
        """Calcula juros compostos com aportes mensais"""
        monthly_rate = (1 + rate/100) ** (1/12) - 1
        months = years * 12
        
        # Cálculo do valor futuro
        future_value_initial = initial * (1 + monthly_rate) ** months
        future_value_monthly = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        total_value = future_value_initial + future_value_monthly
        
        # Total investido
        total_invested = initial + (monthly * months)
        
        # Ganhos
        earnings = total_value - total_invested
        
        # Projeção anual
        projection = []
        for year in range(1, years + 1):
            year_months = year * 12
            fv_initial = initial * (1 + monthly_rate) ** year_months
            fv_monthly = monthly * (((1 + monthly_rate) ** year_months - 1) / monthly_rate)
            year_total = fv_initial + fv_monthly
            projection.append({
                "ano": year,
                "valor_acumulado": round(year_total, 2),
                "total_investido": initial + (monthly * year_months),
                "ganhos": round(year_total - (initial + (monthly * year_months)), 2)
            })
        
        return {
            "valor_final": round(total_value, 2),
            "total_investido": round(total_invested, 2),
            "ganhos_juros": round(earnings, 2),
            "taxa_anual": rate,
            "projecao_anual": projection,
            "retorno_percentual": round((earnings / total_invested) * 100, 2)
        }
    
    def get_suggested_rates(self, perfil: str) -> Dict[str, float]:
        """Retorna taxas sugeridas baseadas no perfil e Selic atual"""
        base_rates = {
            "conservador": 0.85,  # 85% da Selic
            "moderado": 1.1,      # 110% da Selic  
            "agressivo": 1.3      # 130% da Selic
        }
        return base_rates.get(perfil, 1.0)
    
    async def simulate_investment(self, simulation_data: Dict) -> Dict:
        """Executa simulação completa de investimento"""
        # Se taxa não for fornecida, usa Selic + perfil
        if not simulation_data.get('taxa_anual'):
            selic_rate = await self.get_selic_rate()
            suggested_rate = selic_rate * self.get_suggested_rates(simulation_data['perfil_risco'])
            simulation_data['taxa_anual'] = round(suggested_rate, 2)
        
        result = self.calculate_compound_interest(
            initial=simulation_data['valor_inicial'],
            monthly=simulation_data['aporte_mensal'],
            years=simulation_data['tempo_anos'],
            rate=simulation_data['taxa_anual']
        )
        
        return {
            **result,
            "dados_simulacao": simulation_data,
            "timestamp": datetime.now().isoformat()
        }