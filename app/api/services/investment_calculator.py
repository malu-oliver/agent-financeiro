import math
from typing import List, Dict, Any
from app.api.services.selic_api import SelicAPI, MockSelicAPI

class InvestmentCalculator:
    def __init__(self):
        try:
            self.selic_api = SelicAPI()
        except:
            self.selic_api = MockSelicAPI()

    async def calculate_compound_interest(self, initial: float, monthly: float, years: int, rate: float) -> Dict[str, Any]:
        """Calcula juros compostos com aportes mensais"""
        try:
            monthly_rate = rate / 12 / 100
            months = years * 12
            
            future_value = initial * math.pow(1 + monthly_rate, months)
            
            for month in range(months):
                future_value += monthly * math.pow(1 + monthly_rate, months - month - 1)
            
            total_invested = initial + (monthly * months)
            interest_earned = future_value - total_invested

            return {
                "valor_final": round(future_value, 2),
                "total_investido": round(total_invested, 2),
                "juros_acumulados": round(interest_earned, 2),
                "taxa_anual": rate,
                "meses": months
            }
        except Exception as e:
            print(f"Erro no cálculo de juros: {e}")
            return {
                "valor_final": initial + (monthly * years * 12),
                "total_investido": initial + (monthly * years * 12),
                "juros_acumulados": 0,
                "taxa_anual": rate,
                "meses": years * 12
            }

    async def simulate_investment_scenarios(self, initial: float, monthly: float, years: int, profile: str) -> Dict[str, Any]:
        """Simula investimentos baseado no perfil"""
        try:
            # Taxas baseadas no perfil
            profile_rates = {
                "conservador": 0.08,  # 8% ao ano (Selic + CDI)
                "moderado": 0.12,     # 12% ao ano
                "agressivo": 0.18     # 18% ao ano
            }
            
            base_rate = profile_rates.get(profile, 0.10)
            
            # Obtém taxa Selic atual para comparação
            current_selic = await self.selic_api.get_current_selic() or 0.1175
            
            scenarios = {}
            
            # Cenário do perfil
            scenarios["perfil"] = await self.calculate_compound_interest(initial, monthly, years, base_rate)
            
            # Cenário otimista
            scenarios["otimista"] = await self.calculate_compound_interest(initial, monthly, years, base_rate * 1.25)
            
            # Cenário pessimista
            scenarios["pessimista"] = await self.calculate_compound_interest(initial, monthly, years, base_rate * 0.75)
            
            # Cenário Selic (conservador)
            scenarios["selic"] = await self.calculate_compound_interest(initial, monthly, years, current_selic * 100)
            
            scenarios["taxa_selic_atual"] = current_selic * 100
            scenarios["projecao_mensal"] = self.generate_monthly_projection(initial, monthly, years, base_rate)
            
            return scenarios
            
        except Exception as e:
            print(f"Erro na simulação de investimentos: {e}")
            return {"erro": "Não foi possível simular os investimentos"}

    def generate_monthly_projection(self, initial: float, monthly: float, years: int, rate: float) -> List[Dict[str, float]]:
        """Gera projeção ano a ano"""
        try:
            monthly_rate = rate / 12 / 100
            months = years * 12
            projection = []
            
            current_value = initial
            
            for year in range(1, years + 1):
                for month in range(12):
                    current_value = (current_value + monthly) * (1 + monthly_rate)
                
                projection.append({
                    "ano": year,
                    "valor_acumulado": round(current_value, 2),
                    "total_investido": initial + (monthly * year * 12)
                })
            
            return projection
        except Exception as e:
            print(f"Erro na projeção mensal: {e}")
            return []